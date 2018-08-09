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
    
    def process_input(self, main_search=None, artist_search=None, instrument=None):
        all_instruments = self.get_instruments()

        words = main_search.split(' ') if main_search else []
        instruments = []
        partial_instruments = []

        if words:
            words = [i.upper() for i in words]
            if 'SAX' in words:
                words.append('ALTO SAX')
                words.append('BARITONE SAX')
                words.append('SOPRANO SAX')
                words.append('TENOR SAX')
                words.remove('SAX')

            instruments = [i.upper() for i in words if i.upper() in all_instruments]
            if not instruments:
                partial_instruments = [i.upper() for i in words if any(item.startswith(i.upper()) for item in all_instruments)]
                partial_instruments = [i for i in partial_instruments if i not in instruments]
            words = [i for i in words if i.upper() not in instruments]
        
        if artist_search:
            words = artist_search.split(' ')
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
                temp_sqs = sqs.filter(first_name__istartswith=words[0],
                                      last_name__istartswith=words[1]).distinct()
                if temp_sqs.count() == 0:
                    temp_sqs = sqs.filter(first_name__istartswith=words[1],
                                          last_name__istartswith=words[0]).distinct()
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
                    last_name__istartswith=word) | Q(
                    first_name__istartswith=word)
                for word in words:
                    condition |= Q(
                        last_name__istartswith=word) | Q(
                        first_name__istartswith=word)
                sqs = sqs.filter(condition).distinct()
    
        return sqs


    def search_event(self, main_search, order=None, date=None):
        order = {
            'newest': '-start',
            'oldest': 'start',
            'popular': 'popular',
        }.get(order, '-start')

        sqs = Event.objects.all()
        words = main_search.split(' ')
        all_instruments = self.get_instruments()
        instruments = [i for i in words if i.upper() in all_instruments]

        if instruments:
            condition = Q(artists_gig_info__role__name__icontains=instruments[0],
                          artists_gig_info__is_leader=True)
            for i in instruments[1:]:
                condition |= Q(artists_gig_info__role__name__icontains=i,
                               artists_gig_info__is_leader=True)
            sqs = Event.objects.filter(condition).distinct()

        if words:
            artist = words.pop()
            condition = Q(
                title__icontains=artist) | Q(
                description__icontains=artist) | Q(
                performers__first_name__icontains=artist) | Q(
                performers__last_name__icontains=artist)
            for artist in words:
                condition |= Q(
                    title__icontains=artist) | Q(
                    description__icontains=artist) | Q(
                    performers__first_name__icontains=artist) | Q(
                    performers__last_name__icontains=artist)
            sqs = sqs.filter(condition).distinct()

        sqs = sqs.filter(recordings__media_file__isnull=False,
                         recordings__state=Recording.STATUS.Published)

        if date:
            # Force hours to start of day
            date = date.replace(hour=10, minute=0, second=0, microsecond=0)
            sqs = sqs.filter(start__gte=date)

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
