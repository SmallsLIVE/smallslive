from datetime import timedelta
import pytest
from django.utils import timezone

from events.factories import EventFactory


@pytest.fixture
def event():
    return EventFactory()


@pytest.mark.django_db
class TestEvent:
    def test_get_absolute_url(self, event):
        assert event.get_absolute_url() == u'/events/50-a-test-event/'

    def test_is_past(self, event):
        assert event.is_past is True

        event.end = timezone.datetime(2099, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())
        assert event.is_past is False

    def test_listing_date(self, event):
        assert event.listing_date() == event.start.date()

        # after midnight should belong to day before
        event.start = timezone.datetime(2014, 12, 10, 1, 30, 0, tzinfo=timezone.get_current_timezone())
        assert event.listing_date() == (event.start.date() - timedelta(days=1))

        # early morning belongs to next day
        event.start = timezone.datetime(2014, 12, 11, 7, 0, 0, tzinfo=timezone.get_current_timezone())
        assert event.listing_date() == (event.start.date())

    def test_early_morning(self, event):
        assert event.is_early_morning() is False

        # after midnight should belong to day before
        event.start = timezone.datetime(2014, 12, 10, 1, 30, 0, tzinfo=timezone.get_current_timezone())
        assert event.is_early_morning() is True

        # early morning belongs to next day
        event.start = timezone.datetime(2014, 12, 11, 7, 0, 0, tzinfo=timezone.get_current_timezone())
        assert event.is_early_morning() is False

    def test_status_css_class(self, event):
        assert event.status_css_class() == 'label-success'

        event.state = 'Draft'
        assert event.status_css_class() == 'label-warning'

        event.state = 'Cancelled'
        assert event.status_css_class() == 'label-danger'

        event.state = 'Hidden'
        assert event.status_css_class() == 'label-default'

    def test_sidemen_string(self, event):
        assert event.artists_gig_info.count() == 3
