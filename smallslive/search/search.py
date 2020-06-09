from datetime import timedelta
from django.db.models import Count, Q, Sum
from django.utils import timezone
from artists.models import Artist, Instrument
from events.models import Event, Recording


POSSIBLE_NUMBER_OF_PERFORMERS = [
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

SAX_INSTRUMENTS = [
    'ALTO SAX',
    'BARITONE SAX',
    'SOPRANO SAX',
    'TENOR SAX',
]

SAX_INSTRUMENTS_ALIASES_1 = [
    'ALTO SAXOPHONE',
    'BARITONE SAXOPHONE',
    'SOPRANO SAXOPHONE',
    'TENOR SAXOPHONE',
]

SAX_INSTRUMENTS_ALIASES_2 = [
    'ALTO',
    'BARITONE',
    'SOPRANO',
    'TENOR',
]


class SearchObject(object):

    def get_instrument(self, text_array):

        condition = Q(name__icontains=text_array[0])
        for text in text_array[1:]:
            condition |= Q(name__icontains=text)

        return Instrument.objects.filter(condition).distinct()

    def get_instruments(self):

        return map(unicode.upper, Instrument.objects.values_list('name', flat=True))
    
    def filter_sax(self, search_term):
        """Extract SAX, XXX SAX or XXX SAXOPHONE from search_terms"""

        search_term = search_term.upper().strip()
        # User entered specifically sax instruments
        searched_sax_instruments = []
        # User entered 'sax' generically
        all_sax_instruments = []

        # USER ENTERED '<type> SAX'
        for sax in SAX_INSTRUMENTS:
            if sax in search_term:
                # Make sure sax is not an alias before removing from search_terms
                if not [x for x in SAX_INSTRUMENTS_ALIASES_1 if x in search_term and sax in x]:
                    searched_sax_instruments.append(sax)
                    # Remove from search terms
                    search_term = search_term.replace(sax, '')

        # USER ENTERED '<type> SAXOPHONE'
        for sax in SAX_INSTRUMENTS_ALIASES_1:
            if sax in search_term:
                # Make sure 'SAXOPHONE' is stored as 'SAX'
                searched_sax_instruments.append(sax.replace('OPHONE', ''))
                # Remove from search terms
                search_term = search_term.replace(sax, '')

        # USER ENTERED '<type>'
        for index, sax in enumerate(SAX_INSTRUMENTS_ALIASES_2):
            if sax in search_term:
                searched_sax_instruments.append(SAX_INSTRUMENTS[index])
                search_term = search_term.replace(sax, '')

        # User entered only "SAX" or "SAXOPHONE"
        if 'SAX' in search_term or 'SAXOPHONE' in search_term:
            search_term = search_term.replace('SAXOPHONE', '').replace('SAX', '')
            all_sax_instruments = SAX_INSTRUMENTS

        result = search_term, all_sax_instruments, searched_sax_instruments

        return result

    def process_input(self, search_terms=None, artist_search=None, instrument=None):

        all_instruments = self.get_instruments()

        words = []
        all_sax_instruments = []
        instruments = []
        partial_instruments = []

        if search_terms:
            search_terms, all_sax_instruments, instruments = self.filter_sax(search_terms)
            words = search_terms.strip().split(' ')
            words = [x for x in words if x]

        if words:
            words = [i.upper() for i in words]

            instruments += [i.upper() for i in words if i.upper() in all_instruments]
            if not instruments:
                partial_instruments = [i.upper() for i in words
                                       if any(item.startswith(i.upper()) for item in all_instruments)]
                partial_instruments = [i for i in partial_instruments if i not in instruments]

                partial_sax = [i for i in words if 'SAXOPHONE'.startswith(i)]
                if partial_sax:
                    partial_instruments += ['SAX']

            words = [i for i in words if i.upper() not in instruments]

        if artist_search:
            partial_instruments = []
        
        if instrument:
            instruments.append(instrument)
            instruments = [x.upper() for x in instruments]

        instruments = list(set(instruments))

        term_for_artist = None
        number_of_performers = None
        for word in words:
            if word.lower().strip() in POSSIBLE_NUMBER_OF_PERFORMERS:
                number_of_performers = word
                term_for_artist = word

        if number_of_performers in words:
            words.remove(number_of_performers)
            number_of_performers = POSSIBLE_NUMBER_OF_PERFORMERS.index(number_of_performers.lower()) + 1

        first_name = None
        last_name = None
        partial_name = None

        if len(words) == 2:
            first_name, last_name = words
            words = None
        elif len(words) == 1:
            partial_name = words[0]
            words = None

        # In some cases we might have a duplicate in search_terms and artist_search
        if partial_name and artist_search:
            if partial_name.lower() == artist_search.lower():
                partial_name = ''

        # Make sure artist search and names do not overlap
        if artist_search and first_name and artist_search.upper() == first_name.upper():
            partial_name = last_name
            first_name = ''
            last_name = ''
        elif artist_search and last_name and artist_search.upper() == last_name.upper():
            partial_name = first_name
            first_name = ''
            last_name = ''

        return words, instruments, all_sax_instruments, partial_instruments, \
            number_of_performers, first_name, last_name, partial_name, artist_search, term_for_artist

    def filter_artist_instruments(self, instruments, all_sax_instruments):

        if instruments or all_sax_instruments:

            instruments_sqs = None
            if instruments:
                instruments_sqs = Artist.objects.filter(instruments__name__iexact=instruments[0])
                for instrument in instruments[1:]:
                    instruments_sqs &= Artist.objects.filter(instruments__name__iexact=instrument)

            sax_sqs = None
            if all_sax_instruments:
                sax_sqs = Artist.objects.filter(instruments__name__iexact=all_sax_instruments[0])
                for instrument in all_sax_instruments[1:]:
                    sax_sqs |= Artist.objects.filter(instruments__name__iexact=instrument)

            if instruments_sqs is not None and sax_sqs is not None:
                self.sqs = instruments_sqs & sax_sqs
            elif instruments_sqs is not None:
                self.sqs = instruments_sqs
            elif sax_sqs is not None:
                self.sqs = sax_sqs

    def filter_names(self, first_name, last_name):
        temp_sqs = self.sqs.filter(
            first_name__istartswith=first_name,
            last_name__istartswith=last_name
        ).distinct()
        if temp_sqs.count() == 0:
            temp_sqs = self.sqs.filter(
                first_name__istartswith=last_name,
                last_name__istartswith=first_name
            ).distinct()
        self.sqs = temp_sqs

    def filter_partial_name(self, partial_name, artist_search=None):
        condition = Q(last_name__iexact=partial_name)
        if artist_search:
            condition &= Q(first_name__istartswith=artist_search)
        first_name_matches = self.sqs.filter(condition).distinct()
        condition = Q(
            last_name__istartswith=partial_name) & ~Q(
            last_name__iexact=partial_name)
        if artist_search:
            condition &= Q(first_name__istartswith=artist_search)
        good_matches = self.sqs.filter(condition).distinct()

        condition = ~Q(
            last_name__istartswith=partial_name) & Q(
            first_name__istartswith=partial_name) & ~Q(
            last_name__iexact=partial_name)
        if artist_search:
            condition &= Q(last_name__istartswith=artist_search)
        not_so_good_matches = self.sqs.filter(condition).distinct()

        self.sqs = list(first_name_matches) + list(good_matches) + list(not_so_good_matches)

    def filter_partial_instruments(self, partial_instruments):

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

        self.sqs = list(self.sqs) + list(sqs_instruments)

    def filter_artist_names(self, first_name, last_name, partial_name,
                            artist_search, partial_instruments, terms,
                            term_for_artist):

        condition = None
        if artist_search and not partial_name:
            partial_name = artist_search
            artist_search = None

        if first_name and last_name:
            self.filter_names(first_name, last_name)
        elif partial_name:
            self.filter_partial_name(partial_name, artist_search)
            if partial_instruments:
                self.filter_partial_instruments(partial_name)
        elif artist_search:
            for term in terms:
                condition |= Q(
                    last_name__istartswith=term) | Q(
                    first_name__istartswith=term)
            self.sqs = self.sqs.filter(condition).distinct()
        elif term_for_artist:
            self.sqs = Event.objects.none()
            # self.filter_partial_name(term_for_artist)

    def search_artist(self, terms=None,
                      instruments=None, all_sax_instruments=None, partial_instruments=None,
                      first_name=None, last_name=None, partial_name=None, artist_search=None,
                      term_for_artist=None):

        self.sqs = Artist.objects.all().prefetch_related('instruments')
        self.filter_artist_instruments(instruments, all_sax_instruments)
        self.filter_artist_names(first_name, last_name, partial_name,
                                 artist_search, partial_instruments, terms, term_for_artist)

        return self.sqs

    def apply_order(self, sqs, order):

        order = {
            'newest': '-start',
            'oldest': 'start',
            'popular': 'popular',
        }.get(order, '-start')

        if order == 'popular':
            sqs = sqs.order_by('-seconds_played')
        else:
            sqs = sqs.order_by(order)

        return sqs

    def get_leader_condition(self, leader):
        if leader == 'all':
            filter_by_leader = None
        elif leader == 'leader':
            filter_by_leader = True
        else:
            filter_by_leader = False

        if filter_by_leader is not None:
            leader_condition = Q(artists_gig_info__is_leader=filter_by_leader)
        else:
            leader_condition = None

        return leader_condition

    def get_instruments_conditions(self, instruments, all_sax_instruments):

        conditions = []
        if instruments:
            conditions.append(Q(artists_gig_info__role__name__iexact=instruments[0]))
        for instrument in instruments[1:]:
            conditions.append(Q(artists_gig_info__role__name__iexact=instrument))

        return conditions

    def get_names_condition(self, instruments_condition, artist_pk, first_name, last_name,
                             partial_name, artist_search, search_description):

        condition = None
        if artist_pk:
            condition = Q(performers__pk=artist_pk)
        else:
            if first_name and last_name:
                # contains on the title might be slow.
                # only way to match "Brooklyn Circle".
                if search_description:
                    title_cond = Q(title__iucontains=first_name) | \
                                Q(description__iucontains=first_name) | \
                                Q(title__iucontains=last_name) | \
                                Q(description__iucontains=last_name)

                    if not condition:
                        condition = title_cond
                    else:
                        condition |= title_cond
                else:
                    condition = Q(performers__first_name__iexact=first_name,
                                  performers__last_name__iexact=last_name) | \
                                Q(performers__first_name__iexact=last_name,
                                  performers__last_name__iexact=first_name)
            elif search_description and partial_name:
                title_cond = Q(title__iucontains=partial_name) | \
                             Q(description__iucontains=partial_name)
                if not condition:
                    condition = title_cond
                else:
                    condition |= title_cond
            elif partial_name or artist_search:
                performers_first_name_condition = None
                performers_last_name_condition = None
                if partial_name:
                    performers_first_name_condition = Q(performers__first_name__istartswith=partial_name)
                if artist_search:
                    artist_search_condition = Q(performers__last_name__istartswith=artist_search)
                    if performers_first_name_condition:
                        performers_first_name_condition &= artist_search_condition
                    else:
                        performers_first_name_condition = artist_search_condition
                if partial_name:
                    performers_last_name_condition = Q(performers__last_name__istartswith=partial_name)
                if artist_search:
                    artist_search_condition = Q(performers__first_name__istartswith=artist_search)
                    if performers_last_name_condition:
                        performers_last_name_condition &= artist_search_condition
                    else:
                        performers_last_name_condition = artist_search_condition

                if performers_first_name_condition and performers_last_name_condition:
                    condition = performers_first_name_condition | performers_last_name_condition

                if not instruments_condition and not artist_search:
                    desc_condition = Q(title__iucontains=partial_name)
                    if condition:
                        condition |= desc_condition
                    else:
                        condition = desc_condition

        return condition

    def get_names_and_instruments_condition(self, leader_condition, number_of_performers,
                                            instruments_conditions, names_condition):

        names_and_instruments_condition = None

        if names_condition:
            # <name> plays instrument 1 OR <name> plays instrument 2 OR ...
            cond = names_condition & instruments_conditions[0]
            if leader_condition:
                cond &= leader_condition
            for instruments_condition in instruments_conditions[1:]:
                pre_cond = names_condition & instruments_condition
                if leader_condition:
                    pre_cond &= leader_condition
                cond |= pre_cond
            if not number_of_performers:
                self.sqs = self.sqs.filter(cond)
            else:
                names_and_instruments_condition = cond
        else:
            # gig has all instruments provided
            names_and_instruments_condition = []
            for instruments_condition in instruments_conditions:
                if leader_condition:
                    pre_cond = instruments_condition & leader_condition
                else:
                    pre_cond = instruments_condition
                if not number_of_performers:
                    self.sqs = self.sqs.filter(pre_cond)
                else:
                    # We can't filter right now if there are conditions
                    # on the number of performers
                    names_and_instruments_condition.append(pre_cond)

            # require all instruments to be present when
            # filtering number of performers.
            if names_and_instruments_condition:
                cond = names_and_instruments_condition[0]
                for c in names_and_instruments_condition[1:]:
                    cond &= c
                names_and_instruments_condition = cond

        return names_and_instruments_condition

    def filter_number_of_performers(self, leader_condition, number_of_performers,
                                    names_and_instruments_condition, names_condition):

        if names_and_instruments_condition or names_condition:

            # Leader filter was applied before or it wasn't provided.
            if names_and_instruments_condition:
                conditions = names_and_instruments_condition
            elif names_condition:
                conditions = names_condition
            self.sqs = self.sqs\
                .annotate(num_performers=Count('performers', distinct=True)) \
                .filter(Q(num_performers=number_of_performers) & conditions)
        else:
            self.sqs = self.sqs \
                .annotate(num_performers=Count('performers', distinct=True)) \
                .filter(num_performers=number_of_performers)

    def filter_dates(self, start_date, end_date, all_media_status=False):

        today = timezone.localtime(
            timezone.now().replace(hour=0, minute=0, second=0))

        if not start_date or start_date.date() < today.date():
            if not all_media_status:
                self.sqs = self.sqs.filter(
                    recordings__media_file__isnull=False,
                    recordings__state=Recording.STATUS.Published)

        if start_date:
            # Force hours to start of day
            date_from = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
            self.sqs = self.sqs.filter(start__gte=date_from)

        if end_date:
            end_date = end_date + timedelta(days=1)
            date_to = end_date.replace(hour=10, minute=0, second=0, microsecond=0)
            self.sqs = self.sqs.filter(start__lte=date_to)

    def filter_venue(self, venue):
        if venue:
            if venue != 'all':
                self.sqs = self.sqs.filter(venue__pk=venue)

    def search_event(self, terms, order=None, start_date=None, end_date=None,
                     artist_pk=None, venue=None, instruments=None, all_sax_instruments=None,
                     number_of_performers=None, first_name=None, last_name=None,
                     partial_name=None, artist_search=None,
                     leader='all', search_description=False, all_media_status=False):
        """
            number_of_performers: solo, duo, etc. match events by # of performers.
            partial_name: 'john' will match 'john smith' and 'will johnson'
            terms: all terms that are not # of performers, instruments, or names
            artist_search: first letter of an artist name or family name.
            all_sax_instruments: user entered 'sax' forcing the search for any kind of sax.
            search_description: search for event title and description (icontains is a slow operation).
            all_media_status: we need to search for events without media as well.
        """

        self.sqs = Event.objects.get_queryset()

        # Musician has to be a leader. This will apply only if an instrument was selected
        leader_condition = self.get_leader_condition(leader)

        # Get Q objects for instruments.
        instruments_conditions = self.get_instruments_conditions(
            instruments, all_sax_instruments)

        # Get Q objects for matches on names or title
        names_condition = self.get_names_condition(
            instruments_conditions, artist_pk,
            first_name, last_name, partial_name, artist_search, search_description)

        # Get Q objects or apply filter if # performers is provided.
        names_and_instruments_conditions = None
        if instruments_conditions:
            names_and_instruments_conditions = self.get_names_and_instruments_condition(
                leader_condition, number_of_performers,
                instruments_conditions, names_condition)
        else:
            if names_condition:
                if not number_of_performers:
                    if leader_condition:
                        self.sqs = self.sqs.filter(leader_condition, names_condition)
                    else:
                        self.sqs = self.sqs.filter(names_condition)

        # Filter by number of performers (No filter applied yet if # performers provided)
        if number_of_performers:
            self.filter_number_of_performers(
                leader_condition, number_of_performers, names_and_instruments_conditions, names_condition)

        # Filter by venue and dates
        self.filter_venue(venue)
        self.filter_dates(start_date, end_date, all_media_status)
        self.sqs = self.sqs.distinct()

        # Apply sort order
        self.sqs = self.apply_order(self.sqs, order)

        # If no results, set search_description = True to search for event title and description
        # instead of musicians names and instruments.
        if not self.sqs.count() and not search_description:
            self.search_event(
                terms, order, start_date, end_date,
                artist_pk=artist_pk, venue=venue,
                instruments=instruments, all_sax_instruments=all_sax_instruments,
                number_of_performers=number_of_performers,
                first_name=first_name, last_name=last_name, partial_name=partial_name,
                artist_search=artist_search, leader=leader, search_description=True)

        return self.sqs
