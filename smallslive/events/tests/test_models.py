import factory
from factory.django import DjangoModelFactory
import pytest

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key
from events.models import Event



@factory.use_strategy(factory.BUILD_STRATEGY)
class EventFactory(DjangoModelFactory):
    class Meta:
        model = 'events.Event'

    title = u"A test event"


@pytest.mark.django_db
class TestEvent:
    def test_get_absolute_url(self):
        event = mommy.prepare(Event, id=50, title=u"A test event")
        assert event.get_absolute_url() == u'/events/50-a-test-event/'


    def test_is_past(self):
        assert True
