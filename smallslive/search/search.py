from datetime import timedelta
from django.db.models import Q, Sum
from django.utils import timezone
from artists.models import Artist, Instrument
from events.models import Event, Recording

class SearchObject(object):

    def get_instrument(self, text_array):
        print text_array[0]
        condition = Q(name__icontains=text_array[0])
        for text in text_array[1:]:
            condition |= Q(name__icontains=text)
        return Instrument.objects.filter(condition).distinct()

    def get_instruments(self):
        return map(unicode.upper, Instrument.objects.values_list('name', flat=True))
    
    def filter_sax(self, search_term):
        saxs = ['ALTO SAX',
                'BARITONE SAX',
                'SOPRANO SAX',
                'TENOR SAX']

        instruments = []
        search_term = search_term.upper()

        for sax in saxs:
            if sax in search_term:
                instruments.append(sax)
                search_term = search_term.replace(sax, '')
        
        if 'SAX' in search_term or 'SAXOPHONE' in search_term:
            instruments.extend(saxs)
            search_term = search_term.replace('SAXOPHONE', '')
            search_term = search_term.replace('SAX', '')

        return search_term, instruments
    
    def process_input(self, main_search=None, artist_search=None, instrument=None):
        all_instruments = self.get_instruments()

        words = []
        instruments = []
        partial_instruments = []

        if main_search:
            main_search, instruments = self.filter_sax(main_search)
            words = main_search.strip().split(' ')

        if words:
            words = [i.upper() for i in words]

            instruments += [i.upper() for i in words if i.upper() in all_instruments]
            if not instruments:
                partial_instruments = [i.upper() for i in words if any(item.startswith(i.upper()) for item in all_instruments)]
                partial_instruments = [i for i in partial_instruments if i not in instruments]
            words = [i for i in words if i.upper() not in instruments]
        
        if artist_search:
            words = artist_search.strip().split(' ')
            partial_instruments = []
        
        if instrument:
            instruments = [instrument]
            partial_instruments = []

        return words, instruments, partial_instruments

    def search_artist(self, main_search=None, artist_search=None, instrument=None):
        # TODO: use settings to store values
        possible_number_of_performers = ['solo', 'duo', 'trio', 'quartet', 'quintet', 'sextet', 'septet', 'octet', 'nonet', 'dectet']
        if main_search != '':
            if main_search.split()[-1] in possible_number_of_performers:
                main_search = ' '.join(main_search.split()[:-1])

        words, instruments, partial_instruments = self.process_input(main_search, artist_search, instrument)

        sqs = Artist.objects.all()
        
        if instruments:
            condition = Q(instruments__name__istartswith=instruments[0])
            for i in instruments[1:]:
                condition |= Q(instruments__name__istartswith=i)
            sqs = sqs.filter(condition).distinct() 

        if not words:
            return sqs.prefetch_related('instruments')

        if len(words) == 2:
            (first_name, last_name) = words
            temp_sqs = sqs.filter(
                first_name__istartswith=first_name,
                last_name__istartswith=last_name
            ).distinct()
            if temp_sqs.count() == 0:
                temp_sqs = sqs.filter(
                    first_name__istartswith=last_name,
                    last_name__istartswith=first_name
                ).distinct()
            sqs = temp_sqs

        elif len(words) == 1:
            artist = words[0]
            first_name_matches = sqs.filter(Q(
                last_name__iexact=artist)).distinct()
            good_matches = sqs.filter(Q(
                last_name__istartswith=artist) & ~Q(
                last_name__iexact=artist)).distinct()
            not_so_good_matches = sqs.filter(~Q(
                last_name__istartswith=artist) & Q(
                first_name__istartswith=artist) & ~Q(
                last_name__iexact=artist)).distinct()

            sqs = list(first_name_matches) + list(good_matches) + list(not_so_good_matches)

            if partial_instruments:
                condition = Q(instruments__name__istartswith=partial_instruments[0])
                for i in partial_instruments[1:]:
                    condition |= Q(instruments__name__istartswith=i)
                sqs_instruments = Artist.objects.filter(condition).distinct()

                sqs = list(sqs) + list(sqs_instruments)
        else:
            word = words[0]
            condition = Q(
                last_name__istartswith=word) | Q(
                first_name__istartswith=word)
            for word in words:
                condition |= Q(
                    last_name__istartswith=word) | Q(
                    first_name__istartswith=word)
            sqs = sqs.filter(condition).distinct()

        return sqs


    def search_event(self, main_search, order=None, start_date=None, end_date=None,
                     artist_pk=None, venue=None):

        def filter_quantity_of_performers(number_of_performers_searched, artist, just_by_qty):

            events_data = Event.objects.get_events_by_performers_and_artist(
                number_of_performers_searched, artist, just_by_qty)
            event_ids = [x.id for x in events_data]
            
            sqs = Event.objects.filter(pk__in=event_ids)

            return sqs
    
        # sets number_of_performers_searched based in the last word from main_seach
        number_of_performers_searched = None
        # TODO: move this to search settings
        possible_number_of_performers = [
            'solo',
            'duo',
            'trio',
            'quartet',
            'quintet',
            'sextet',
            'septet',
            'octet',
            'nonet',
            'dectet'
        ]

        if main_search != '':
            if main_search.split()[-1] in possible_number_of_performers:
                number_of_performers_searched = possible_number_of_performers.index(main_search.split()[-1]) + 1
                if ''.join(main_search.split()[:-1]) != '' and len(''.join(main_search.split()[:-1])) != 1 :  
                    main_search = ' '.join(main_search.split()[:-1])
            sqs = ''

        order = {
            'newest': '-start',
            'oldest': 'start',
            'popular': 'popular',
        }.get(order, '-start')

        if number_of_performers_searched:
            just_by_qty = False
            if main_search in possible_number_of_performers:
                just_by_qty = True
            sqs = filter_quantity_of_performers(number_of_performers_searched, main_search, just_by_qty)
        elif artist_pk:
            sqs = Event.objects.filter(performers__pk=artist_pk)
        else:
            if not number_of_performers_searched and not len(main_search.split()) == 1:
                sqs = Event.objects.all()
            main_search, instruments = self.filter_sax(main_search)
            words = main_search.strip().split()
            all_instruments = self.get_instruments()
            if words:
                instruments = [i for i in words if i.upper() in all_instruments]
            if instruments:
                condition = Q(artists_gig_info__role__name__icontains=instruments[0],
                            artists_gig_info__is_leader=True)
                for i in instruments[1:]:
                    condition |= Q(artists_gig_info__role__name__icontains=i,
                                artists_gig_info__is_leader=True)
                sqs = Event.objects.filter(condition)

            if words:
                single_artist = False
                if len(words) == 2 and not instruments:
                    temp_sqs = sqs.filter(performers__first_name__iexact=words[0],
                                        performers__last_name__iexact=words[1]).distinct()
                    if temp_sqs.count() == 0:
                        temp_sqs = sqs.filter(performers__first_name__iexact=words[1],
                                            performers__last_name__iexact=words[0]).distinct()
                    if temp_sqs.count() != 0:
                        single_artist = True
                        sqs = temp_sqs
                if not single_artist:
                    artist = words.pop()
                    condition = Q(
                        title__iucontains=artist) | Q(
                        description__iucontains=artist) | Q(
                        performers__first_name__iucontains=artist) | Q(
                        performers__last_name__iucontains=artist)
                    for artist in words:
                        condition |= Q(
                            title__iucontains=artist) | Q(
                            description__iucontains=artist) | Q(
                            performers__first_name__iucontains=artist) | Q(
                            performers__last_name__iucontains=artist)

                if instruments:
                    sqs = sqs | Event.objects.filter(condition)
                elif not single_artist:
                    sqs = Event.objects.filter(condition) 

        sqs = sqs.distinct()

        if venue:
            if venue != 'all':
                sqs = sqs.filter(venue__pk=venue)
                
        # FIXME: compare to code in "today_and_tomorrow_events"
        today = timezone.localtime(
            timezone.now().replace(hour=0, minute=0, second=0))

        if not start_date or start_date.date() < today.date():
            sqs = sqs.filter(recordings__media_file__isnull=False,
                             recordings__state=Recording.STATUS.Published)

        if start_date:
            # Force hours to start of day
            date_from = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
            sqs = sqs.filter(start__gte=date_from)

        if end_date:
            end_date = end_date + timedelta(days=1)
            date_to = end_date.replace(hour=10, minute=0, second=0, microsecond=0)
            sqs = sqs.filter(start__lte=date_to)

        if order == 'popular':
            sqs = sqs.order_by('-seconds_played')
        else:
            sqs = sqs.order_by(order)

        return sqs
