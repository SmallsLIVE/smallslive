from django.views.generic.list import ListView
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

    def get_template_names(self):
        if self.object.is_past():
            template_name = 'events/video.html'
        else:
            template_name = 'events/event_detail.html'
        return [template_name]

event_detail = EventDetailView.as_view()


class VenueDashboardView(ListView):
    queryset = Event.objects.order_by('-end_day')[:50]
    template_name = 'dashboard-admin.html'
    context_object_name = 'events'

venue_dashboard = VenueDashboardView.as_view()
