from django.utils.timezone import datetime, timedelta
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin, UserPassesTestMixin
from extra_views import CreateWithInlinesView, NamedFormsetsMixin, UpdateWithInlinesView

from .forms import EventAddForm, GigPlayedInlineFormSet, GigPlayedInlineFormSetHelper
from .models import Event
from multimedia.models import Media


class HomepageView(TemplateView):
    template_name = 'home.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        today = datetime.now().date()
        few_days_out = today + timedelta(days=3)
        # temporarily removing this so we don't have to generate future events for testing all the time,
        # just show the 5 future events for now
        #context['events'] = Event.objects.filter(start__range=(today, few_days_out)).reverse()
        events = list(Event.objects.all().order_by("-start")[:8])
        events.reverse()
        context['events'] = events
        context['videos'] = Media.objects.order_by('-id')[:5]
        return context

homepage = HomepageView.as_view()


class EventAddView(NamedFormsetsMixin, CreateWithInlinesView):
    template_name = 'events/event_add.html'
    model = Event
    form_class = EventAddForm
    inlines = [GigPlayedInlineFormSet]
    inlines_names = ['artists']

    def get_context_data(self, **kwargs):
        context = super(EventAddView, self).get_context_data(**kwargs)
        context['artists'].helper = GigPlayedInlineFormSetHelper()
        return context

event_add = EventAddView.as_view()


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'events/video.html'
    # def get_template_names(self):
    #     if self.object.is_past():
    #        template_name = 'events/video.html'
    #    else:
    #        template_name = 'events/event_detail.html'
    #    return [template_name]

event_detail = EventDetailView.as_view()


class EventEditView(LoginRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    model = Event
    form_class = EventAddForm
    template_name = 'events/event_edit.html'
    inlines = [GigPlayedInlineFormSet]
    inlines_names = ['artists']

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['artists'].helper = GigPlayedInlineFormSetHelper()
        return context

    # def test_func(self, user):
    #     """
    #     Show 403 forbidden page only when the logged in user doesn't have required
    #     permissions, redirect anonymous users to the login screen.
    #     """
    #     self.raise_exception = True
    #     try:
    #         artist_id_match = self.kwargs.get('pk') == str(user.artist.id)
    #     except Artist.DoesNotExist:
    #         artist_id_match = False
    #     return (artist_id_match or user.is_superuser)

event_edit = EventEditView.as_view()


class VenueDashboardView(ListView):
    queryset = Event.objects.order_by('-modified', '-start')[:50]
    template_name = 'dashboard-admin.html'
    context_object_name = 'events'

venue_dashboard = VenueDashboardView.as_view()


class MyGigsView(ListView):
    """
    Use ListView for easy pagination of past events but also add future events
    to the page context.
    """
    template_name = 'my_gigs.html'
    paginate_by = 20
    context_object_name = 'past_events'

    def get_queryset(self):
        return Event.past.filter(performers=self.request.user.artist)

    def get_context_data(self, **kwargs):
        context = super(MyGigsView, self).get_context_data(**kwargs)
        context['future_events'] = Event.upcoming.filter(performers=self.request.user.artist)
        return context

my_gigs = MyGigsView.as_view()
