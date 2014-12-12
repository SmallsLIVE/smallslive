from datetime import timedelta
import pytest
from django.utils import timezone

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key
from events.models import Event

@pytest.fixture
def event():
    return mommy.prepare(
        Event,
        id=50,
        title=u"A test event",
        start=timezone.datetime(2014, 12, 10, 20, 30, 0, tzinfo=timezone.get_current_timezone()),
        end=timezone.datetime(2014, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())

    )

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
