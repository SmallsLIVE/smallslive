from artists.models import Artist, Instrument
from django.db.models import Q
from events.models import Event, Recording

class SearchObject(object):

    def get_instrument(self, text_array):
        condition = Q(name__icontains=text_array[0])
        for text in text_array[1:]:
            condition |= Q(name__icontains=text)
        return Instrument.objects.filter(condition).distinct().first()

    def get_instruments(self):
        return [i.name.upper() for i in Instrument.objects.all()]

    def search_artist(self, main_search, instrument=None, artist_search=None):
        sqs = Artist.objects.all()
        words = main_search.split(' ')
        all_instruments = self.get_instruments()
        instruments = [i for i in words if any(item.startswith(i.upper()) for item in all_instruments)]
        words = [i for i in words if i not in instruments]

        if instruments:
            condition = Q(instruments__name__istartswith=instruments[0])
            for i in instruments[1:]:
                condition |= Q(instruments__name__istartswith=i)
            sqs = Artist.objects.filter(condition).distinct()

        if instrument:
            sqs = sqs.filter(instruments__name=instrument)

        if words:
            if len(words) > 1:
                if len(words) == 2:
                    exact_sqs = sqs.filter(first_name__iexact=words[0],
                                                 last_name__iexact=words[1]).distinct()
                    if exact_sqs.count() == 0:
                        multiple_search = True
                    else:
                        multiple_search = False
                        sqs = exact_sqs
                    
                else:
                    multiple_search = True

                if multiple_search:
                    artist = words.pop()
                    condition = Q(
                        last_name__icontains=artist) | Q(
                        first_name__icontains=artist)
                    for artist in words:
                        condition |= Q(
                            last_name__icontains=artist) | Q(
                            first_name__icontains=artist)
                    sqs = sqs.filter(condition).distinct()
            else:
                artist = words[0]
                first_name_matches = sqs.filter(Q(
                    first_name__iexact=artist)).distinct()
                good_matches = sqs.filter(Q(
                    first_name__istartswith=artist) & ~Q(
                    first_name__iexact=artist)).distinct()
                not_so_good_matches = sqs.filter(~Q(
                    first_name__istartswith=artist) & Q(
                    last_name__istartswith=artist) & ~Q(
                    first_name__iexact=artist)).distinct()
                sqs =  list(first_name_matches) + list(good_matches) + list(not_so_good_matches)

        artist_words = None
        if artist_search:
            artist_words = artist_search.split(' ')
            artist_words = [i for i in artist_words if i not in instruments]

            if len(artist_words) == 1:
                artist = artist_words[0]
                good_matches = sqs.filter(Q(
                    last_name__istartswith=artist)).distinct()
                not_so_good_matches = sqs.filter(~Q(
                    last_name__istartswith=artist) & Q(
                    first_name__istartswith=artist)).distinct()
                sqs = list(good_matches) + list(not_so_good_matches)

            elif len(artist_words) > 1:
                if len(artist_words) == 2:
                    exact_sqs = sqs.filter(first_name__iexact=artist_words[0],
                                                 last_name__iexact=artist_words[1]).distinct()
                    if exact_sqs.count() == 0:
                        multiple_search = True
                    else:
                        multiple_search = False
                        sqs = exact_sqs

                else:
                    multiple_search = True

                if multiple_search:
                    artist = artist_words.pop()
                    condition = Q(
                        last_name__icontains=artist) | Q(
                        first_name__icontains=artist)
                    for artist in artist_words:
                        condition |= Q(
                            last_name__icontains=artist) | Q(
                            first_name__icontains=artist)
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
            sqs = sqs.most_popular()
        else:
            sqs = sqs.order_by(order)
        
        return sqs
