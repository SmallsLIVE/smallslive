import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin, UserPassesTestMixin
from extra_views import CreateWithInlinesView, NamedFormsetsMixin, UpdateWithInlinesView

from smallslive.artists.models import Artist
from smallslive.multimedia.models import Media

from .forms import EventAddForm, GigPlayedAddInlineFormSet, GigPlayedInlineFormSetHelper, GigPlayedEditInlineFormset
from .models import Event


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
    inlines = [GigPlayedAddInlineFormSet]
    inlines_names = ['artists']

    def get_context_data(self, **kwargs):
        context = super(EventAddView, self).get_context_data(**kwargs)
        context['artists'].helper = GigPlayedInlineFormSetHelper()
        context['show_times'] = json.dumps(settings.SHOW_TIMES)
        return context

event_add = EventAddView.as_view()


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'events/video.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['performers'] = self.object.get_performers()
        return context

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
    inlines = [GigPlayedEditInlineFormset]
    inlines_names = ['artists']

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['artists'].helper = GigPlayedInlineFormSetHelper()
        context['show_times'] = json.dumps(settings.SHOW_TIMES)
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


class EventCloneView(LoginRequiredMixin, SuperuserRequiredMixin, BaseDetailView):
    model = Event

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        gig_info = self.object.get_performers()
        new_object = self.object
        new_object.pk = None
        new_object.state = Event.STATUS.Draft
        new_object.save()
        for info in gig_info:
            info.pk = None
            info.event = new_object
            info.save()
        self.extra_event_processing(new_object)
        self.new_object = new_object
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('event_edit', kwargs={'pk': self.new_object.id, 'slug': slugify(self.new_object.title)})

    def extra_event_processing(self, event):
        """
        Overridable method meant for extra event processing such as cloning the tickets or doing
        some other manipulation on the newly cloned event object.
        """
        pass

event_clone = EventCloneView.as_view()


class VenueDashboardView(ListView):
    queryset = Event.objects.order_by('-modified', '-start')[:50]
    template_name = 'dashboard-admin.html'
    context_object_name = 'events'

venue_dashboard = VenueDashboardView.as_view()


class MyGigsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Use ListView for easy pagination of past events but also add future events
    to the page context.
    """
    template_name = 'my_gigs.html'
    paginate_by = 50
    context_object_name = 'past_events'

    def get_queryset(self):
        return Event.past.filter(performers=self.request.user.artist)

    def get_context_data(self, **kwargs):
        context = super(MyGigsView, self).get_context_data(**kwargs)
        context['future_events'] = Event.upcoming.filter(performers=self.request.user.artist)
        return context

    def test_func(self, user):
        """
        Checks if the logged in user is also an artist.
        """
        self.raise_exception = True
        return user.is_artist

my_gigs = MyGigsView.as_view()


class CalendarView(ListView):
    template_name = 'calendar.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.all().order_by("-start")[:30]

calendar = CalendarView.as_view()


class Recordings(ListView):
    """
    Temporary code from brian to get some events on page:
    """
    queryset = Event.objects.order_by('-start')[:50]
    template_name = 'video-manager.html'
    context_object_name = 'past_events'

recordings = Recordings.as_view()


class ArtistVideoManager(ListView):
    """
    Temporary code from brian to get some events on page:
    """
    queryset = Event.objects.order_by('-start')[:50]
    template_name = 'musician-signup-choose-videos.html'
    context_object_name = 'past_events'

artist_video_manager = ArtistVideoManager.as_view()