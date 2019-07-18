from collections import OrderedDict
from itertools import groupby
import calendar
import hashlib
from datetime import time as std_time
from cacheops import cached
from django.core import signing
from django.db.models import Count
import monthdelta
import json
import time
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import connection
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import DeleteView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView, BaseDetailView

from django_ajax.mixin import AJAXMixin
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin, StaffuserRequiredMixin
from extra_views import CreateWithInlinesView, NamedFormsetsMixin, UpdateWithInlinesView
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from haystack.views import SearchView
from rest_framework.authtoken.models import Token

from artists.models import Artist, Instrument
from metrics.models import UserVideoMetric
from oscar_apps.catalogue.models import Product
from search.utils import facets_by_model_name
from .forms import EventAddForm, GigPlayedAddInlineFormSet, GigPlayedInlineFormSetHelper, GigPlayedEditInlineFormset, \
    EventSearchForm, EventEditForm
from .models import Event, Recording


class HomepageView(ListView):
    template_name = 'home.html'
    context_object_name = 'events_today'

    def get_queryset(self):
        date_range_start = timezone.localtime(timezone.now()).replace(hour=5, minute=0)
        date_range_end = date_range_start + timedelta(days=1)
        return Event.objects.filter(start__gte=date_range_start, start__lte=date_range_end).order_by('start')

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        date_range_start = timezone.localtime(timezone.now())
        # if it's not night when events are still hapenning, show next day
        if date_range_start.hour > 6:
            date_range_start += timedelta(days=1)
        # don't show last nights events that are technically today
        date_range_start = date_range_start.replace(hour=10)
        events = Event.objects.filter(start__gte=date_range_start).order_by('start')
        if not self.request.user.is_staff:
            events = events.exclude(state=Event.STATUS.Draft)
        # 30 events should be enough to show next 7 days with events
        events = events[:30]
        dates = {}
        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)
        # next 7 days
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0])).items()[:7]
        context['new_in_archive'] = Event.objects.most_recent()[:8]
        context['next_7_days'] = sorted_dates

        @cached(timeout=6*60*60)
        def _get_most_popular():
            context = {}
            most_popular_ids = UserVideoMetric.objects.most_popular(count=4, weekly=True)
            most_popular = []
            for event_data in most_popular_ids:
                try:
                    event = Event.objects.get(id=event_data['event_id'])
                    most_popular.append(event)
                except Event.DoesNotExist:
                    pass
            context['popular_in_archive'] = most_popular
            return context

        context.update(_get_most_popular())
        context['popular_in_store'] = [] # Product.objects.filter(featured=True, product_class__slug='album')[:6]
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
    queryset = Event.objects.all().select_related('recording', 'recording__media_file')
    context_object_name = 'event'
    template_name = 'events/event_details_new.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['performers'] = self.object.get_performers()
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID
        context['metrics_ping_interval'] = settings.PING_INTERVAL
        context['metrics_server_url'] = settings.METRICS_SERVER_URL
        context['metrics_signed_data'] = self._generate_metrics_data()
        if self.request.user.is_authenticated():
            context['user_token'] = Token.objects.get(user=self.request.user)
            user_is_artist = self.request.user.is_artist and self.request.user.artist in self.object.performers.all()
            user_is_staff = self.request.user.is_staff
            if user_is_artist or user_is_staff:
                context['count_metrics'] = False
            else:
                context['count_metrics'] = True
        return context

    def _generate_metrics_data(self):
        data = {}
        for rec in self.object.recordings.all():
            rec_data = {
                'recording_id': rec.id,
                'recording_type': rec.media_file.media_type.upper()[0],
                'event_id': self.object.id,
                'user_id': self.request.user.id,
            }
            signed_value = signing.dumps(rec_data)
            data[rec.id] = signed_value
        return data

event_detail = EventDetailView.as_view()


class EventEditView(NamedFormsetsMixin, UpdateWithInlinesView):
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

event_edit = staff_member_required(EventEditView.as_view())


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
        sqs = self.sqs.models(Event).load_all_queryset(Event, Event.objects.all().annotate(product_count=Count('products')).extra(select={
            'video_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='video'"
                           " GROUP BY events_event.id",
            'audio_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='audio'"
                           " GROUP BY events_event.id",
        }))
        return sqs


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

        events = events.annotate(product_count=Count('products')).extra(select={
            'video_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='video'"
                           " GROUP BY events_event.id",
            'audio_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='audio'"
                           " GROUP BY events_event.id",
        })
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
        events = events.annotate(product_count=Count('products')).extra(select={
            'video_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='video'"
                           " GROUP BY events_event.id",
            'audio_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='audio'"
                           " GROUP BY events_event.id",
        })
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
            end_range_date = date + timedelta(days=1)
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
        tomorrow = now
        if not now.hour < 6:
            tomorrow = now + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=6)
        events = list(Event.objects.public().filter(end__gte=now,
                                                    start__lte=tomorrow).order_by('start'))
        return events

    def get_context_data(self, **kwargs):
        now = timezone.localtime(timezone.now())
        context = super(LiveStreamView, self).get_context_data(**kwargs)
        TRESHOLD = 30
        # also include todays events that have finished
        if now.hour < 6:
            start_range = (now - timedelta(days=1)).replace(hour=6)
            end_range = now.replace(hour=6)

        else:
            start_range = now.replace(hour=6)
            end_range = (now + timedelta(days=1)).replace(hour=6)
        todays_events = Event.objects.public().filter(start__gte=start_range,
                                                    start__lte=end_range).order_by('start')
        # currently playing or future events, showed for displaying "coming up"
        if context['events'] and context['events'][0].has_started():
            context['currently_playing'] = context['events'].pop(0)

        context['first_future_show'] = Event.objects.filter(start__gte=timezone.now()).order_by('start').first()

        return context

live_stream = LiveStreamView.as_view()


class MezzrowLiveStreamView(TemplateView):
    template_name = 'events/live-stream-mezzrow.html'

    def get_context_data(self, **kwargs):
        context = super(MezzrowLiveStreamView, self).get_context_data(**kwargs)
        now = timezone.localtime(timezone.now())
        stream_turn_off_hour = 2
        stream_turn_on_hour = 17
        context['hide_stream'] = stream_turn_off_hour <= now.hour <= stream_turn_on_hour
        return context

live_stream_mezzrow = MezzrowLiveStreamView.as_view()


class ArchiveView(ListView):
    template_name = "events/archive.html"
    context_object_name = 'date_events'

    def get_queryset(self):
        two_week_interval = int(self.request.GET.get('week', 0)) * 14

        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT(e.start::date) FROM "events_event" AS e INNER JOIN "events_recording" AS rec'
                       ' ON e.id=rec.event_id WHERE date_part(\'hour\', e.start) > 12 ORDER BY start DESC LIMIT 14 OFFSET %s', [two_week_interval])
        dates = [d[0] for d in cursor.fetchall()]
        date_range_start = datetime.combine(dates[-1], std_time(10, 0))
        self.date_start = date_range_start
        date_range_end = dates[0] + timedelta(days=1)
        date_range_end = datetime.combine(date_range_end, std_time(4, 0))
        events = Event.objects.exclude(recordings=None).filter(start__gte=date_range_start, start__lte=date_range_end).order_by('start')
        if not self.request.user.is_staff:
            events = events.exclude(state=Event.STATUS.Draft)

        events = events.annotate(product_count=Count('products')).extra(select={
            'video_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='video'"
                           " GROUP BY events_event.id",
            'audio_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='audio'"
                           " GROUP BY events_event.id",
        })
        dates = {}
        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0])).items()
        return sorted_dates

    def get_context_data(self, **kwargs):
        context = super(ArchiveView, self).get_context_data(**kwargs)

        @cached(timeout=6*60*60)
        def _get_most_popular():
            context = {}
            context['most_recent'] = Event.objects.most_recent()[:12]

            weekly_most_popular_ids = UserVideoMetric.objects.most_popular(count=12, weekly=False)
            weekly_most_popular = []
            for event_data in weekly_most_popular_ids:
                try:
                    event = Event.objects.get(id=event_data['event_id'])
                    weekly_most_popular.append(event)
                except Event.DoesNotExist:
                    pass
            context['most_popular'] = weekly_most_popular

            return context

        context['month'] = self.date_start.month - 1
        context['year'] = self.date_start.year
        context.update(_get_most_popular())
        context.update(self.get_pagination())
        return context

    def get_pagination(self):
        context = {}
        week = int(self.request.GET.get('week', 0))
        context['prev_url'] = "{0}?week={1}".format(reverse('archive'), week + 1)
        if week > 1:
            context['next_url'] = "{0}?week={1}".format(reverse('archive'), week - 1)
        else:
            context['next_url'] = reverse('archive')
        return context


archive = ArchiveView.as_view()


class MonthlyArchiveView(ArchiveView):
    def get_queryset(self):
        dates = {}
        month = int(self.kwargs.get('month', timezone.now().month))
        year = int(self.kwargs.get('year', timezone.now().year))
        # don't show last nights events that are technically today
        date_range_start = timezone.make_aware(timezone.datetime(year, month, 1, hour=10),
                                               timezone.get_default_timezone())
        self.date_start = date_range_start
        date_range_end = date_range_start + monthdelta.MonthDelta(1)
        events = Event.objects.exclude(recordings=None).filter(start__range=(date_range_start, date_range_end)).order_by('start')
        if not self.request.user.is_staff:
            events = events.exclude(state=Event.STATUS.Draft)
        events = events.annotate(product_count=Count('products')).extra(select={
            'video_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='video'"
                           " GROUP BY events_event.id",
            'audio_count': "SELECT COUNT(*) FROM events_recording, multimedia_mediafile WHERE "
                           "events_recording.event_id = events_event. ID AND "
                           "events_recording.media_file_id = multimedia_mediafile. ID AND "
                           " events_recording. STATE = 'Published' AND multimedia_mediafile.media_type='audio'"
                           " GROUP BY events_event.id",
        })
        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0])).items()
        return sorted_dates

    def get_pagination(self):
        context = {}
        # js months are zero indexed
        month = int(self.kwargs.get('month', timezone.now().month))
        year = int(self.kwargs.get('year', timezone.now().year))
        context['month'] = month - 1
        context['year'] = year
        context['month_view'] = True
        # position of the "NEXT" box, after all the dates and the "PREV" box
        current_month = timezone.datetime(year=year, month=month, day=1)
        next_month = current_month + timezone.timedelta(days=31)
        prev_month = current_month - timezone.timedelta(days=1)
        context['prev_url'] = reverse('monthly_archive', kwargs={'year': prev_month.year, 'month': prev_month.month})
        context['next_url'] = reverse('monthly_archive', kwargs={'year': next_month.year, 'month': next_month.month})
        return context

monthly_archive = MonthlyArchiveView.as_view()
