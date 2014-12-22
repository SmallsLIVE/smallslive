from django.utils import timezone
import factory
from .models import Event


class ArtistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'artists.Artist'

    first_name = factory.Sequence(lambda n: u'First#{0}'.format(n))
    last_name = factory.Sequence(lambda n: u'Last#{0}'.format(n))


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Sequence(lambda n: u'A test event {0}'.format(n))
    start = timezone.datetime(2014, 12, 10, 20, 30, 0, tzinfo=timezone.get_current_timezone())
    end = timezone.datetime(2014, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())
    state = 'Published'


class InstrumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'artists.Instrument'

    name = factory.Iterator(['Trumpet', 'Bass', 'Piano'])
    abbreviation = factory.Iterator(['tr', 'b', 'p'])


class GigPlayedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.GigPlayed'

    artist = factory.SubFactory(ArtistFactory)
    event = factory.SubFactory(EventFactory)
    role = factory.SubFactory(InstrumentFactory)


class EventWithPerformersFactory(EventFactory):
    gig_1 = factory.RelatedFactory(GigPlayedFactory, 'event')
    gig_2 = factory.RelatedFactory(GigPlayedFactory, 'event')
    gig_3 = factory.RelatedFactory(GigPlayedFactory, 'event')