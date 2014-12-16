import factory
from .models import Event


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    id = 50
    title = u'A test event'
