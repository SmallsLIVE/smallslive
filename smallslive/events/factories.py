from django.utils import timezone
import factory
from artists.factories import ArtistFactory, InstrumentFactory


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.Event'

    title = factory.Sequence(lambda n: u'A test event {0}'.format(n))
    start = timezone.datetime(2016, 12, 10, 20, 30, 0, tzinfo=timezone.get_current_timezone())
    end = timezone.datetime(2016, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())
    state = 'Published'

    @classmethod
    def _setup_next_sequence(self):
        return 1


class PastEventFactory(EventFactory):
    start = timezone.datetime(2000, 12, 10, 20, 30, 0, tzinfo=timezone.get_current_timezone())
    end = timezone.datetime(2000, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())


class GigPlayedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.GigPlayed'

    artist = factory.SubFactory(ArtistFactory)
    role = factory.SubFactory(InstrumentFactory)
    event = factory.SubFactory(EventFactory)

    @classmethod
    def _setup_next_sequence(self):
        return 1


class PastGigPlayedFactory(GigPlayedFactory):
    event = factory.SubFactory(PastEventFactory)


class EventWithPerformersFactory(EventFactory):
    gig_1 = factory.RelatedFactory(GigPlayedFactory, 'event', is_leader=True)
    gig_2 = factory.RelatedFactory(GigPlayedFactory, 'event')
    gig_3 = factory.RelatedFactory(GigPlayedFactory, 'event')


class PastEventWithPerformersFactory(PastEventFactory):
    gig_1 = factory.RelatedFactory(GigPlayedFactory, 'event', is_leader=True)
    gig_2 = factory.RelatedFactory(GigPlayedFactory, 'event')
    gig_3 = factory.RelatedFactory(GigPlayedFactory, 'event')
