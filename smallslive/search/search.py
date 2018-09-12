from artists.models import Artist, Instrument
from django.db.models import Q, Sum
from events.models import Event, Recording
from metrics.models import UserVideoMetric

class SearchObject(object):

    def get_instrument(self, text_array):
        condition = Q(name__icontains=text_array[0])
        for text in text_array[1:]:
            condition |= Q(name__icontains=text)
        return Instrument.objects.filter(condition).distinct().first()

    def get_instruments(self):
        return [i.name.upper() for i in Instrument.objects.all()]
    
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
        words, instruments, partial_instruments = self.process_input(main_search, artist_search, instrument)

        sqs = Artist.objects.all()

        if instruments:
            condition = Q(instruments__name__istartswith=instruments[0])
            for i in instruments[1:]:
                condition |= Q(instruments__name__istartswith=i)
            sqs = sqs.filter(condition).distinct()

        if words:
            if len(words) == 2:
                temp_sqs = sqs.filter(first_name__iustartswith=words[0],
                                      last_name__iustartswith=words[1]).distinct()
                if temp_sqs.count() == 0:
                    temp_sqs = sqs.filter(first_name__iustartswith=words[1],
                                          last_name__iustartswith=words[0]).distinct()
                sqs = temp_sqs
            elif len(words) == 1:

                artist = words[0]
                first_name_matches = sqs.filter(Q(
                    last_name__iuexact=artist)).distinct()
                good_matches = sqs.filter(Q(
                    last_name__iustartswith=artist) & ~Q(
                    last_name__iuexact=artist)).distinct()
                not_so_good_matches = sqs.filter(~Q(
                    last_name__iustartswith=artist) & Q(
                    first_name__iustartswith=artist) & ~Q(
                    last_name__iuexact=artist)).distinct()

                sqs =  list(first_name_matches) + list(good_matches) + list(not_so_good_matches)

                if partial_instruments:
                    condition = Q(instruments__name__istartswith=partial_instruments[0])
                    for i in partial_instruments[1:]:
                        condition |= Q(instruments__name__istartswith=i)
                    sqs_instruments = Artist.objects.filter(condition).distinct()

                    sqs = list(sqs) + list(sqs_instruments)
            else:
                word = words[0]
                condition = Q(
                    last_name__iustartswith=word) | Q(
                    first_name__iustartswith=word)
                for word in words:
                    condition |= Q(
                        last_name__iustartswith=word) | Q(
                        first_name__iustartswith=word)
                sqs = sqs.filter(condition).distinct()
    
        return sqs


    def search_event(self, main_search, order=None, date_from=None, date_to=None):
        order = {
            'newest': '-start',
            'oldest': 'start',
            'popular': 'popular',
        }.get(order, '-start')

        sqs = Event.objects.all()
        instruments = []
        main_search, instruments = self.filter_sax(main_search)
        words = main_search.strip().split()
        all_instruments = self.get_instruments()
        instruments += [i for i in words if i.upper() in all_instruments]

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
                temp_sqs = sqs.filter(performers__first_name__iuexact=words[0],
                                      performers__last_name__iuexact=words[1]).distinct()
                if temp_sqs.count() == 0:
                    temp_sqs = sqs.filter(performers__first_name__iuexact=words[1],
                                          performers__last_name__iuexact=words[0]).distinct()
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

        sqs = sqs.filter(recordings__media_file__isnull=False,
                         recordings__state=Recording.STATUS.Published)

        if date_from and date_to:
            # Force hours to start of day
            date_from = date_from.replace(hour=10, minute=0, second=0, microsecond=0)
            sqs = sqs.filter(start__gte=date_from)

            date_to = date_to.replace(hour=10, minute=0, second=0, microsecond=0)
            sqs = sqs.filter(start__lte=date_to)

        if order == 'popular':
            # TODO Duplicated in event/views
            # Special case, we need to use metrics db
            event_map = dict([
                (event.id, event) for event in sqs.all()
            ])

            # Order metrics
            most_popular_ids = UserVideoMetric.objects.filter(
                event_id__in=event_map.keys()
            ).values('event_id').annotate(
                count=Sum('seconds_played')
            ).order_by('-count')

            most_popular = []
            for event_data in most_popular_ids:
                event_id = event_data['event_id']
                most_popular.append(event_map[event_id])

            return most_popular

        else:
            sqs = sqs.order_by(order)

        return sqs
