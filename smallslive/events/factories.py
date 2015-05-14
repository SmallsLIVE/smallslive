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


class GigPlayedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.GigPlayed'

    artist = factory.SubFactory(ArtistFactory)
    role = factory.SubFactory(InstrumentFactory)
    event = factory.SubFactory(EventFactory)
    is_leader = False

    @classmethod
    def _setup_next_sequence(self):
        return 1


class PastEventFactory(EventFactory):
    start = timezone.datetime(2000, 12, 10, 20, 30, 0, tzinfo=timezone.get_current_timezone())
    end = timezone.datetime(2000, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())


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


class AudioMediaFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'multimedia.MediaFile'

    file = factory.Sequence(lambda n: u'file{0}.mp3'.format(n))
    media_type = 'audio'
    format = 'mp3'


class RecordingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.Recording'

    set_number = factory.Sequence(lambda n: n)


class AudioRecordingFactory(RecordingFactory):
    media_file = factory.SubFactory(AudioMediaFileFactory)


class VideoMediaFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'multimedia.MediaFile'

    file = factory.Sequence(lambda n: u'{0}.mp4'.format(n))
    sd_video_file = factory.Sequence(lambda n: u'360p/{0}_360p.mp4'.format(n))
    media_type = 'video'
    format = 'mp4'


class VideoRecordingFactory(RecordingFactory):
    media_file = factory.SubFactory(VideoMediaFileFactory)


class PastEventWithMediaFactory(PastEventFactory):
    @factory.post_generation
    def media(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        AudioRecordingFactory.create_batch(3, event=self)
        VideoRecordingFactory.create_batch(2, event=self)


class PastGigPlayedWithMediaFactory(GigPlayedFactory):
    event = factory.SubFactory(PastEventWithMediaFactory)
