from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from .models import Event


class EventAddView(TemplateView):
    template_name = 'events/event_add.html'

event_add = EventAddView.as_view()


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

event_detail = EventDetailView.as_view()
