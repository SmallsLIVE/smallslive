from datetime import timedelta
from django.db.models import Count, Q, Sum
from django.utils import timezone
from artists.models import Artist, Instrument
from events.models import Event, Recording


class SearchObject(object):

    def get_instrument(self, text_array):
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

        words = search_term.split(' ')
        words = [x for x in words if x]
        if 'SAX' in words or 'SAXOPHONE' in words:
            instruments.extend(saxs)
            search_term = search_term.replace('SAXOPHONE', '')
            search_term = search_term.replace('SAX', '')

        return search_term, instruments
    
    def process_input(self, search_terms=None, artist_search=None, instrument=None):

        all_instruments = self.get_instruments()

        words = []
        instruments = []
        partial_instruments = []
        possible_number_of_performers = ['solo', 'duo', 'trio', 'quartet', 'quintet', 'sextet', 'septet', 'octet',
                                         'nonet', 'dectet']

        if search_terms:
            search_terms, instruments = self.filter_sax(search_terms)
            words = search_terms.strip().split(' ')
        if words:
            words = [i.upper() for i in words]

            instruments += [i.upper() for i in words if i.upper() in all_instruments]
            if not instruments:
                partial_instruments = [i.upper() for i in words if any(item.startswith(i.upper()) for item in all_instruments)]
                partial_instruments = [i for i in partial_instruments if i not in instruments]

                partial_sax = [i for i in words if 'SAXOPHONE'.startswith(i)]
                if partial_sax:
                    partial_instruments += ['SAX']

            words = [i for i in words if i.upper() not in instruments]

        if artist_search:
            partial_instruments = []
        
        if instrument:
            instruments = [instrument]
            partial_instruments = []

        number_of_performers = None
        for word in words:
            if word.lower().strip() in possible_number_of_performers:
                number_of_performers = word

        if number_of_performers in words:
            words.remove(number_of_performers)
            number_of_performers = possible_number_of_performers.index(number_of_performers.lower()) + 1

        first_name = None
        last_name = None
        partial_name = None

        if len(words) == 2:
            first_name, last_name = words
            words = None
        elif len(words) == 1:
            partial_name = words[0]
            words = None

        return words, instruments, partial_instruments, number_of_performers, first_name, last_name, partial_name, artist_search

    def search_artist(self, terms=None,
                      instruments=None, partial_instruments=None,
                      first_name=None, last_name=None, partial_name=None, artist_search=None):

        print '******************  search_artist : ********************'
        print 'terms: ', terms
        print 'instruments: ', instruments
        print 'first name: ', first_name
        print 'last name: ', last_name
        print 'partial instruments: ', partial_instruments
        print 'partial name: ', partial_name, type(partial_name)
        print 'artist_search: ', artist_search, type(artist_search)
        print '------------------------------------------------------'

        sqs = Artist.objects.all()

        if instruments:
            condition = Q(instruments__name__icontains=instruments[0])
            for i in instruments[1:]:
                condition |= Q(instruments__name__icontains=i)

            # instruments containing sax are a special case
            no_sax_instruments = [x for x in instruments if 'SAX' not in x]
            sax_instruments = [x for x in instruments if 'SAX' in x]
            instruments_count = len(no_sax_instruments)
            if sax_instruments:
                instruments_count += 1

            sqs = sqs.filter(condition).annotate(
                num_instruments=Count('instruments')).filter(num_instruments=instruments_count)

        if artist_search and not partial_name:
            partial_name = artist_search
            artist_search = None

        if not terms and not first_name and not last_name and not partial_name and not instruments:
            return sqs.prefetch_related('instruments')

        if first_name and last_name:
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

        elif partial_name:
            condition = Q(last_name__iexact=partial_name)
            if artist_search:
                condition &= Q(first_name__istartswith=artist_search)
            first_name_matches = sqs.filter(condition).distinct()
            condition = Q(
                last_name__istartswith=partial_name) & ~Q(
                last_name__iexact=partial_name)
            if artist_search:
                condition &= Q(first_name__istartswith=artist_search)
            good_matches = sqs.filter(condition).distinct()

            condition = ~Q(
                last_name__istartswith=partial_name) & Q(
                first_name__istartswith=partial_name) & ~Q(
                last_name__iexact=partial_name)
            if artist_search:
                condition &= Q(last_name__istartswith=artist_search)
            not_so_good_matches = sqs.filter(condition).distinct()

            sqs = list(first_name_matches) + list(good_matches) + list(not_so_good_matches)

            if partial_instruments:
                if 'SAX' == partial_instruments[0]:
                    condition = Q(instruments__name__icontains=partial_instruments[0])
                else:
                    condition = Q(instruments__name__istartswith=partial_instruments[0])
                for i in partial_instruments[1:]:
                    if i == 'SAX':
                        condition |= Q(instruments__name__icontains=i)
                    else:
                        condition |= Q(instruments__name__istartswith=i)
                sqs_instruments = Artist.objects.filter(condition).distinct()

                sqs = list(sqs) + list(sqs_instruments)
        elif artist_search:
            for term in terms:
                condition |= Q(
                    last_name__istartswith=term) | Q(
                    first_name__istartswith=term)
            sqs = sqs.filter(condition).distinct()

        return sqs

    def filter_quantity_of_performers(self, number_of_performers, first_name, last_name, partial_name, instruments):

        if first_name and last_name or partial_name:
            events_data = Event.objects.get_events_by_performers_and_artist(
                number_of_performers, first_name, last_name, partial_name
            )
        elif instruments:
            events_data = Event.objects.get_events_by_performers_and_instrument(
                number_of_performers, instruments
            )

        event_ids = [x.id for x in events_data]
        sqs = Event.objects.filter(pk__in=event_ids)

        return sqs

    def get_queryset(self, terms, artist_pk=None, instruments=None, number_of_performers=None,
                     first_name=None, last_name=None, partial_name=None, artist_search=None,
                     leader='all'):

        sqs = Event.objects.get_queryset()

        if leader == 'all':
            filter_by_leader = None
        elif leader == 'leader':
            filter_by_leader = True
        else:
            filter_by_leader = False

        if instruments:
            if filter_by_leader is None:
                instruments_condition = Q(artists_gig_info__role__name__icontains=instruments[0])
                for i in instruments[1:]:
                    instruments_condition |= Q(artists_gig_info__role__name__icontains=i)
            else:
                instruments_condition = Q(artists_gig_info__role__name__icontains=instruments[0],
                                          artists_gig_info__is_leader=filter_by_leader)
                for i in instruments[1:]:
                    instruments_condition |= Q(artists_gig_info__role__name__icontains=i,
                                               artists_gig_info__is_leader=filter_by_leader)

        elif filter_by_leader is not None:

            instruments_condition = Q(artists_gig_info__is_leader=filter_by_leader)
        else:
            instruments_condition = None

        if artist_pk:
            if instruments_condition:
                instruments_condition &= Q(performers__pk=artist_pk)
                sqs = sqs.filter(instruments_condition)
            else:
                sqs = sqs.filter(performers__pk=artist_pk)
        else:
            if number_of_performers:
                sqs = self.filter_quantity_of_performers(
                    number_of_performers, first_name, last_name, partial_name, instruments)
            else:
                if first_name and last_name:
                    condition = Q(performers__first_name__iexact=first_name,
                                  performers__last_name__iexact=last_name)
                    temp_sqs = sqs.filter(condition).distinct()
                    if temp_sqs.count() == 0:
                        condition = Q(performers__first_name__iexact=last_name,
                                      performers__last_name__iexact=first_name)
                    if instruments_condition:
                        condition &= instruments_condition

                elif partial_name:

                    performers_first_name_condition = Q(performers__first_name__istartswith=partial_name)
                    if artist_search:
                        performers_first_name_condition &= Q(performers__last_name__istartswith=artist_search)
                    if instruments_condition:
                        performers_first_name_condition &= instruments_condition
                    performers_last_name_condition = Q(performers__last_name__istartswith=partial_name)
                    if artist_search:
                        performers_last_name_condition &= Q(performers__first_name__istartswith=artist_search)
                    if instruments_condition:
                        performers_last_name_condition &= instruments_condition

                    condition = Q(
                        performers_first_name_condition) | Q(
                        performers_last_name_condition)

                    if not instruments_condition and not artist_search:
                        condition |= Q(
                            title__iucontains=partial_name) | Q(
                            description__iucontains=partial_name)
                elif artist_search:
                    performers_first_name_condition = Q(performers__last_name__istartswith=artist_search)
                    if instruments_condition:
                        performers_first_name_condition &= instruments_condition
                    performers_last_name_condition = Q(performers__first_name__istartswith=artist_search)
                    if instruments_condition:
                        performers_last_name_condition &= instruments_condition

                    condition = Q(
                        performers_first_name_condition) | Q(
                        performers_last_name_condition)

                elif terms:
                    term = terms[0]
                    condition = Q(
                        title__iucontains=term) | Q(
                        description__iucontains=term) | Q(
                        performers__first_name__iucontains=term) | Q(
                        performers__last_name__iucontains=term)
                    for term in terms[1:]:
                        condition |= Q(
                            title__iucontains=term) | Q(
                            description__iucontains=term) | Q(
                            performers__first_name__iucontains=term) | Q(
                            performers__last_name__iucontains=term)
                else:
                    condition = instruments_condition

                if condition:
                    sqs = sqs.filter(condition)

        sqs = sqs.distinct()

        print sqs.query

        return sqs

    def search_event(self, terms, order=None, start_date=None, end_date=None,
                     artist_pk=None, venue=None, instruments=None, number_of_performers=None,
                     first_name=None, last_name=None, partial_name=None, artist_search=None,
                     leader='all'):

        order = {
            'newest': '-start',
            'oldest': 'start',
            'popular': 'popular',
        }.get(order, '-start')

        sqs = self.get_queryset(
            terms, artist_pk, instruments, number_of_performers,
            first_name, last_name, partial_name, artist_search, leader)

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
