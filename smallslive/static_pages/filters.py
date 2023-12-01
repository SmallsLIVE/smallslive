import django_filters
from django.db.models import Q
from events.models import Event

class ArchiveFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Event
        fields = ['title']
        strict = False

    def __init__(self, *args, **kwargs):
        super(ArchiveFilter, self).__init__(*args, **kwargs)

    @property
    def form(self):
        form = super(ArchiveFilter, self).form  
        form.fields['title'].widget.attrs['class'] = 'form-control search'
        form.fields['title'].widget.attrs['placeholder'] = 'Search by event name'
        return form


class EventsListFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Event
        fields = ['title']
        strict = False

    def __init__(self, *args, **kwargs):
        super(EventsListFilter, self).__init__(*args, **kwargs)

    @property
    def form(self):
        form = super(EventsListFilter, self).form  
        form.fields['title'].widget.attrs['class'] = 'form-control search'
        form.fields['title'].widget.attrs['placeholder'] = 'Search by event name'
        return form