import pytest
from django.core import mail
from users.models import SmallsEmailAddress
from events.factories import EventFactory, GigPlayedFactory

from ..factories import ArtistFactory, ArtistWithEventsFactory, ArtistWithMediaFactory, InstrumentFactory


@pytest.fixture(scope="module")
def artist_factory():
    return ArtistFactory


@pytest.fixture(scope="module")
def artist_with_events_factory():
    return ArtistWithEventsFactory


@pytest.fixture(scope="module")
def artist_with_events_and_media_factory():
    return ArtistWithMediaFactory


@pytest.fixture(autouse=True)
@pytest.mark.django_db()
def reset_model_counters():
    ArtistFactory.reset_sequence()
    GigPlayedFactory.reset_sequence()
    EventFactory.reset_sequence()
    InstrumentFactory.reset_sequence()
    InstrumentFactory.name.reset()
    InstrumentFactory.abbreviation.reset()


@pytest.mark.django_db()
class TestArtist:
    def test_get_absolute_url(self, artist_factory):
        artist = artist_factory.create()
        assert artist.get_absolute_url() == u'/artists/1-first1-last1/'

        another_artist = artist_factory.create()
        assert another_artist.get_absolute_url() == u'/artists/2-first2-last2/'

    def test_full_name(self, artist_factory):
        artist = artist_factory.build()
        assert artist.full_name() == u'First#1 Last#1'

        another_artist = artist_factory.build()
        assert another_artist.full_name() == u'First#2 Last#2'

    def test_upcoming_events(self, artist_with_events_factory):
        artist = artist_with_events_factory.create()
        assert artist.events.count() == 5
        assert artist.upcoming_events().count() == 3
        assert "A test event 1" in artist.upcoming_events().values_list('title', flat=True)
        assert "A test event 2" in artist.upcoming_events().values_list('title', flat=True)
        assert "A test event 3" in artist.upcoming_events().values_list('title', flat=True)

    def test_past_events(self, artist_with_events_factory):
        artist = artist_with_events_factory.create()
        assert artist.events.count() == 5
        assert artist.past_events().count() == 2
        assert "A test event 4" in artist.past_events().values_list('title', flat=True)
        assert "A test event 5" in artist.past_events().values_list('title', flat=True)

    def test_get_instruments(self, artist_factory):
        artist = artist_factory.create()
        assert artist.instruments.count() == 3
        assert artist.get_instruments() == "Trumpet\nBass\nPiano"

    def test_get_main_instrument_name(self, artist_factory):
        artist = artist_factory.create()
        assert artist.get_main_instrument_name() == "Trumpet"

        artist.instruments.all().delete()
        assert artist.get_main_instrument_name() == ""

    def test_events_count(self, artist_with_events_factory):
        artist = artist_with_events_factory.create()
        assert artist.events_count() == 5

    def test_media_count(self, artist_with_events_and_media_factory):
        artist = artist_with_events_and_media_factory.create()
        # 2 events with 3 audio and 2 video each = 10
        assert artist.media_count() == 10

    def test_send_invitation(self, artist_factory, django_user_model, rf):
        # artist without a User model assigned
        request = rf.get('artist_add')
        email = "test@example.com"
        artist = artist_factory.create()
        artist.send_invitation(request, email=email)
        assert artist.user.id == 1
        assert SmallsEmailAddress.objects.filter(email=email, user=artist.user).count() == 1
        assert len(mail.outbox) == 1
        assert "Confirm E-mail Address" in mail.outbox[0].subject

        # User already exists in the DB
        email = "test2@example.com"
        django_user_model.objects.create_user(email=email)
        another_artist = artist_factory.create()
        another_artist.send_invitation(request, email=email)
        assert another_artist.user.id == 2
        assert SmallsEmailAddress.objects.filter(email=email, user=another_artist.user).count() == 1
        assert len(mail.outbox) == 2
        assert "Confirm E-mail Address" in mail.outbox[1].subject

    def test_auto_slugifying(self, artist_factory):
        artist = artist_factory.create()
        assert artist.slug == "first1-last1"

        artist.slug = "test-slug-should-stay-same"
        artist.save()
        assert artist.slug == "test-slug-should-stay-same"

    def test_autocomplete_labels(self, artist_factory):
        artist = artist_factory.create()
        assert artist.autocomplete_label() == "First#1 Last#1"
        assert artist.autocomplete_sublabel() == "Trumpet"

    # def test_is_leader_for_event(self, artist_with_events_factory):
    #     artist = artist_with_events_factory.create()
    #     leader_event = Event.objects.get(id=1)
    #     assert artist.is_leader_for_event(leader_event)
    #
    #     nonleader_event = Event.objects.get(id=2)
    #     assert not artist.is_leader_for_event(nonleader_event)

    def test_photo_crop_box(self, artist_factory):
        artist = artist_factory.build()
        artist.cropping = "100,100,300,400"
        assert artist.photo_crop_box == (('100', '100'), ('300', '400'))

        artist = artist_factory.build()
        artist.cropping = ""
        assert not artist.photo_crop_box

        artist = artist_factory.build()
        artist.cropping = "-50,50,100,100"
        assert not artist.photo_crop_box