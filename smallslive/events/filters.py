import django_filters
from .models import Event

class EventFilter(django_filters.FilterSet):
    venue = django_filters.NumberFilter(field_name='venue__id')

    class Meta:
        model = Event
        fields = ['venue']
