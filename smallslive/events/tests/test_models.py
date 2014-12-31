from datetime import timedelta
import pytest
from django.utils import timezone
from artists.factories import ArtistFactory
from ..factories import GigPlayedFactory, EventFactory, EventWithPerformersFactory


@pytest.fixture(scope="module")
def event_factory():
    return EventFactory


@pytest.fixture(scope="module")
def full_event_factory():
    # event with performers, saved to DB, has ID
    return EventWithPerformersFactory

@pytest.fixture(autouse=True)
@pytest.mark.django_db()
def reset_model_counters():
    EventFactory.reset_sequence()
    ArtistFactory.reset_sequence()
    GigPlayedFactory.reset_sequence()


@pytest.mark.django_db()
class TestEvent:
    def test_get_absolute_url(self, full_event_factory):
        event = full_event_factory.create()
        assert event.get_absolute_url() == u'/events/1-a-test-event-1/'

        another_event = full_event_factory.create()
        assert another_event.get_absolute_url() == u'/events/2-a-test-event-2/'

    def test_is_past(self, event_factory):
        event = event_factory.build()
        assert event.is_past is True

        event.end = timezone.datetime(2099, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())
        assert event.is_past is False

    def test_listing_date(self, event_factory):
        event = event_factory.build()
        assert event.listing_date() == event.start.date()

        # after midnight should belong to day before
        event.start = timezone.datetime(2014, 12, 10, 1, 30, 0, tzinfo=timezone.get_current_timezone())
        assert event.listing_date() == (event.start.date() - timedelta(days=1))

        # early morning belongs to next day
        event.start = timezone.datetime(2014, 12, 11, 7, 0, 0, tzinfo=timezone.get_current_timezone())
        assert event.listing_date() == (event.start.date())

    def test_early_morning(self, event_factory):
        event = event_factory.build()
        assert event.is_early_morning() is False

        # after midnight should belong to day before
        event.start = timezone.datetime(2014, 12, 10, 1, 30, 0, tzinfo=timezone.get_current_timezone())
        assert event.is_early_morning() is True

        # early morning belongs to next day
        event.start = timezone.datetime(2014, 12, 11, 7, 0, 0, tzinfo=timezone.get_current_timezone())
        assert event.is_early_morning() is False

    def test_status_css_class(self, event_factory):
        event = event_factory.build()
        assert event.status_css_class() == 'label-success'

        event.state = 'Draft'
        assert event.status_css_class() == 'label-warning'

        event.state = 'Cancelled'
        assert event.status_css_class() == 'label-danger'

        event.state = 'Hidden'
        assert event.status_css_class() == 'label-default'

    def test_performers_string(self, full_event_factory):
        event = full_event_factory.create()
        assert event.performers_string() == "First#1 Last#1, First#2 Last#2, First#3 Last#3"

    def test_performers_with_instruments_string(self, full_event_factory):
        event = full_event_factory.create()
        assert event.performers_with_instruments_string() == "First#1 Last#1 (tr), First#2 Last#2 (b), First#3 Last#3 (p)"

    def test_sidemen_string(self, full_event_factory):
        event = full_event_factory.create()
        assert event.sidemen_string() == "First#2 Last#2, First#3 Last#3"

    def test_sidemen_with_instruments_string(self, full_event_factory):
        event = full_event_factory.create()
        assert event.sidemen_with_instruments_string() == "First#2 Last#2 (b), First#3 Last#3 (p)"

    def test_leader_string(self, full_event_factory):
        event = full_event_factory.create()
        assert event.leader_string() == "First#1 Last#1"

        event.artists_gig_info.all().update(is_leader=False)
        assert event.leader_string() == ""

    def test_leader_with_instrument_string(self, full_event_factory):
        event = full_event_factory.create()
        assert event.leader_with_instrument_string() == "First#1 Last#1 (tr)"

        event.artists_gig_info.all().update(is_leader=False)
        assert event.leader_with_instrument_string() == ""

    def test_display_title(self, full_event_factory):
        # event with preassigned title
        event = full_event_factory.create()
        assert event.display_title() == "A test event 1 w/ First#1 Last#1, First#2 Last#2, First#3 Last#3"

        # event with no title
        event.title = None
        assert event.display_title() == "First#1 Last#1 w/ First#2 Last#2, First#3 Last#3"

        # event with no title and no leader
        event.artists_gig_info.all().update(is_leader=False)
        assert event.display_title() == "First#1 Last#1, First#2 Last#2, First#3 Last#3"

    def test_display_title_with_instruments(self, full_event_factory):
        # event with preassigned title
        event = full_event_factory.create()
        assert event.display_title_with_instruments() == "A test event 1 w/ First#1 Last#1 (tr), First#2 Last#2 (b), First#3 Last#3 (p)"

        # event with no title
        event.title = None
        assert event.display_title_with_instruments() == "First#1 Last#1 (tr) w/ First#2 Last#2 (b), First#3 Last#3 (p)"

        # event with no title and no leader
        event.artists_gig_info.all().update(is_leader=False)
        assert event.display_title_with_instruments() == "First#1 Last#1 (tr), First#2 Last#2 (b), First#3 Last#3 (p)"
