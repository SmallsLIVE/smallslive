from django.utils.timezone import datetime, timedelta
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .models import Event
from multimedia.models import Media


class HomepageView(TemplateView):
    template_name = 'home.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        today = datetime.now().date()
        week_from_today = today + timedelta(weeks=1)
        context['events'] = Event.objects.filter(start_day__range=(today, week_from_today)).reverse()
        context['videos'] = Media.objects.order_by('-id')[:5]
        return context

homepage = HomepageView.as_view()


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
    queryset = Event.objects.order_by('-modified', '-start_day')[:50]
    template_name = 'dashboard-admin.html'
    context_object_name = 'events'

venue_dashboard = VenueDashboardView.as_view()


class MyGigsView(TemplateView):
    template_name = 'my_gigs.html'

    def get_context_data(self, **kwargs):
        context = super(MyGigsView, self).get_context_data(**kwargs)
        context['past_events'] = Event.past.all()[:50]
        context['future_events'] = Event.future.all()[:50]
        return context

my_gigs = MyGigsView.as_view()
