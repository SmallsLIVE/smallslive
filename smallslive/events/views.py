from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from .models import Event


class EventAddView(CreateView):
    template_name = 'events/event_add.html'
    model = Event

event_add = EventAddView.as_view()


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

event_detail = EventDetailView.as_view()
