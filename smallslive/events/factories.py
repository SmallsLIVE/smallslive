from django.utils import timezone
import factory
from .models import Event


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    id = 50
    title = u'A test event'
    start = timezone.datetime(2014, 12, 10, 20, 30, 0, tzinfo=timezone.get_current_timezone())
    end = timezone.datetime(2014, 12, 10, 22, 30, 0, tzinfo=timezone.get_current_timezone())
    state = 'Published'
