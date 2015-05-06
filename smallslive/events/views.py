from collections import OrderedDict
from itertools import groupby
from operator import itemgetter, attrgetter
import calendar
import hashlib
from django.db import connection
import monthdelta
import json
import time
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.template.defaulttags import regroup
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta
from django.views.generic import DeleteView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView, BaseDetailView

from django_ajax.mixin import AJAXMixin
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin, StaffuserRequiredMixin
from extra_views import CreateWithInlinesView, NamedFormsetsMixin, UpdateWithInlinesView
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from haystack.views import SearchView

from artists.models import Artist, Instrument
from search.utils import facets_by_model_name
from .forms import EventAddForm, GigPlayedAddInlineFormSet, GigPlayedInlineFormSetHelper, GigPlayedEditInlineFormset, \
    EventSearchForm, EventEditForm
from .models import Event, Recording


class HomepageView(ListView):
    template_name = 'home.html'
    context_object_name = 'events'

    def get_queryset(self):
        date_range_start = timezone.localtime(timezone.now()).replace(hour=5, minute=0)
        date_range_end = date_range_start + timedelta(days=1)
        return Event.objects.filter(start__gte=date_range_start, start__lte=date_range_end).order_by('start')

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        start = timezone.localtime(timezone.now()) - timedelta(hours=4)
        context['dates'] = [start + timedelta(days=d) for d in range(5)]
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT EXTRACT( DAY FROM start) from events_event WHERE EXTRACT(MONTH FROM start) = %s AND EXTRACT(YEAR FROM start) = %s AND state='Published'", [start.month, start.year])
        days_with_events = cursor.fetchall()
        days_with_events = [int(x[0]) for x in days_with_events]
        context['disabled_dates'] = ['{}/{}/{}'.format(start.month, x, start.year) for x in range(1, 30) if x not in days_with_events]
        return context

homepage = HomepageView.as_view()


class EventAddView(StaffuserRequiredMixin, NamedFormsetsMixin, CreateWithInlinesView):
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
    template_name = 'events/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['performers'] = self.object.get_performers()
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID
        return context

event_detail = EventDetailView.as_view()


class EventEditView(StaffuserRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    model = Event
    form_class = EventEditForm
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


class EventDeleteView(StaffuserRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('home')

event_delete = EventDeleteView.as_view()


class EventCloneView(StaffuserRequiredMixin, BaseDetailView):
    model = Event

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        old_event_id = self.object.id
        gig_info = self.object.get_performers()
        new_object = self.object
        new_object.pk = None
        new_object.state = Event.STATUS.Draft
        new_object.save()
        for info in gig_info:
            info.pk = None
            info.event = new_object
            info.save()
        self.extra_event_processing(new_object, old_event_id)
        self.new_object = new_object
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('event_edit', kwargs={'pk': self.new_object.id, 'slug': slugify(self.new_object.title)})

    def extra_event_processing(self, event, old_event_id):
        """
        Overridable method meant for extra event processing such as cloning the tickets or doing
        some other manipulation on the newly cloned event object.
        """
        pass

event_clone = EventCloneView.as_view()


class EventSearchView(SearchView):
    template = 'search/event_search.html'

    def extra_context(self):
        context = {}
        paginator, page = self.build_page()
        adjacent_pages = 2
        startPage = max(page.number - adjacent_pages, 1)
        if startPage <= 3:
            startPage = 1
        endPage = page.number + adjacent_pages + 1
        if endPage >= paginator.num_pages - 1:
            endPage = paginator.num_pages + 1
        page_numbers = [n for n in xrange(startPage, endPage) if n > 0 and n <= paginator.num_pages]
        context.update({
            'page_numbers': page_numbers,
            'show_first': 1 not in page_numbers,
            'show_last': paginator.num_pages not in page_numbers,
            })

        context['counts'] = facets_by_model_name(self.sqs)

        artist_id = self.request.GET.get('artist')
        if artist_id:
            search_term = Artist.objects.get(id=artist_id).full_name()
        else:
            search_term = self.request.GET.get('q')
        context['search_term'] = search_term

        return context

    def get_results(self):
        self.sqs = super(EventSearchView, self).get_results().facet('model', order='term').order_by('-start')
        return self.sqs.models(Event)

event_search = EventSearchView(
    form_class=EventSearchForm,
    searchqueryset=RelatedSearchQuerySet()
)


class ScheduleView(ListView):
    context_object_name = 'dates'
    template_name = 'events/schedule.html'

    def get_queryset(self):
        """
        The view returns a list of events in two week intervals, for both the home page
        and the "next" links. The correct two week interval is set through the URL or by
        default it's a two week interval from the current date. The admin user sees all future
        events immediately, regardless of date intervals and event status.
        """
        dates = {}
        two_week_interval = int(self.request.GET.get('week', 0))
        start_days = two_week_interval * 14
        date_range_start = timezone.localtime(timezone.now()) + timezone.timedelta(days=start_days)
        # don't show last nights events that are technically today
        date_range_start = date_range_start.replace(hour=10)
        self.date_start = date_range_start
        date_range_end = date_range_start + timezone.timedelta(days=14)
        events = Event.objects.filter(start__gte=date_range_start, start__lte=date_range_end).order_by('start')
        if not self.request.user.is_staff:
            events = events.exclude(state=Event.STATUS.Draft)
        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)
        for date in [(date_range_start + timedelta(days=d)).date() for d in range(14)]:
            if date not in dates:
                dates[date] = []
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0]))
        return sorted_dates

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        # js months are zero indexed
        context['month'] = self.date_start.month - 1
        context['year'] = self.date_start.year
        week = int(self.request.GET.get('week', 0))
        if week != 1:
            context['prev_url'] = "{0}?week={1}".format(reverse('schedule'), week-1)
        else:
            context['prev_url'] = reverse('schedule')
        if week == -1:
            context['next_url'] = reverse('schedule')
        else:
            context['next_url'] = "{0}?week={1}".format(reverse('schedule'), week+1)
        return context

schedule = ScheduleView.as_view()


class MonthlyScheduleView(ListView):
    context_object_name = 'dates'
    template_name = 'events/schedule.html'

    def get_queryset(self):
        dates = {}
        month = int(self.kwargs.get('month', timezone.now().month))
        year = int(self.kwargs.get('year', timezone.now().year))
        # don't show last nights events that are technically today
        date_range_start = timezone.make_aware(timezone.datetime(year, month, 1, hour=10),
                                               timezone.get_default_timezone())
        date_range_end = date_range_start + monthdelta.MonthDelta(1)
        last_day_of_month = calendar.monthrange(year, month)[1]
        events = Event.objects.filter(start__range=(date_range_start, date_range_end)).order_by('start')
        if not self.request.user.is_staff:
            events = events.exclude(state=Event.STATUS.Draft)
        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)
        for date in [(date_range_start + timedelta(days=d)).date() for d in range(last_day_of_month)]:
            if date not in dates:
                dates[date] = []
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0]))
        return sorted_dates

    def get_context_data(self, **kwargs):
        """
        Timedelta doesn't support months so to get the next and previous months, we do a max delta (31 days) for the
        next month, and a min one (1 day) for the previous month.
        """
        context = super(MonthlyScheduleView, self).get_context_data(**kwargs)
        # js months are zero indexed
        month = int(self.kwargs.get('month', timezone.now().month))
        year = int(self.kwargs.get('year', timezone.now().year))
        context['month'] = month - 1
        context['year'] = year
        context['month_view'] = True
        # position of the "NEXT" box, after all the dates and the "PREV" box
        context['next_month_position'] = len(context['dates']) + 2
        current_month = timezone.datetime(year=year, month=month, day=1)
        next_month = current_month + timezone.timedelta(days=31)
        prev_month = current_month - timezone.timedelta(days=1)
        context['prev_url'] = reverse('monthly_schedule', kwargs={'year': prev_month.year, 'month': prev_month.month})
        context['next_url'] = reverse('monthly_schedule', kwargs={'year': next_month.year, 'month': next_month.month})
        return context

monthly_schedule = MonthlyScheduleView.as_view()


class ScheduleCarouselAjaxView(AJAXMixin, DetailView):
    context_object_name = 'event'
    model = Event
    template_name = "blocks/schedule-event-details-carousel.html"

schedule_carousel_ajax = ScheduleCarouselAjaxView.as_view()


class HomepageEventCarouselAjaxView(AJAXMixin, ListView):
    context_object_name = 'events'
    template_name = "blocks/homepage-upcoming-events-carousel.html"

    def get_queryset(self):
        date = self.request.GET.get('date')
        if date and date != "undefined":
            date = timezone.make_aware(datetime.strptime(date, "%m/%d/%Y").replace(hour=6, minute=0),
                                       timezone.get_current_timezone())
            print date
            end_range_date = date + timedelta(days=1)
            print end_range_date
            events = Event.objects.filter(start__range=(date, end_range_date)).order_by('start')
            if not self.request.user.is_staff:
                events = events.exclude(state=Event.STATUS.Draft)
            return events
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super(HomepageEventCarouselAjaxView, self).get_context_data(**kwargs)
        if self.request.GET.get("template") == "home":
            start = timezone.localtime(timezone.now()) - timedelta(hours=4)
            context['dates'] = [start + timedelta(days=d) for d in range(5)]
        return context

event_carousel_ajax = HomepageEventCarouselAjaxView.as_view()


class LiveStreamView(ListView):
    context_object_name = "events"
    template_name = "events/live-stream.html"

    def get_queryset(self):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=6)
        events = list(Event.objects.public().filter(end__gte=now,
                                                    start__lte=tomorrow).order_by('start'))
        return events

    def get_context_data(self, **kwargs):
        context = super(LiveStreamView, self).get_context_data(**kwargs)
        if context['events'] and context['events'][0].has_started():
            context['currently_playing'] = context['events'].pop(0)
        context['first_future_show'] = Event.objects.filter(start__gte=timezone.now()).order_by('start').first()
        context['stream_expire'] = int(time.time()) + 10  # 10 seconds - required just to start the stream
        context['stream_hash'] = hashlib.md5("{0}{1}?e={2}".format(settings.BITGRAVITY_SECRET, "/smallslive/secure/",
                                                                   context['stream_expire'])).hexdigest()
        return context

live_stream = LiveStreamView.as_view()


class ArchiveView(TemplateView):
    template_name = "events/archive.html"
    
    def get_context_data(self, **kwargs):
        context = super(ArchiveView, self).get_context_data(**kwargs)
        context['recent_audio'] = Recording.objects.audio().order_by('-date_added')[:4]
        context['most_popular_audio'] = Recording.objects.audio().order_by('-view_count')[:4]
        context['recent_video'] = Recording.objects.video().order_by('-date_added')[:4]
        context['most_popular_video'] = Recording.objects.video().order_by('-view_count')[:4]
        return context

archive = ArchiveView.as_view()