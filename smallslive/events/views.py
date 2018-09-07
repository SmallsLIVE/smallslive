from collections import OrderedDict
from itertools import groupby
import calendar
import datetime
from datetime import time as std_time
from cacheops import cached
from django.core import signing
from django.db.models import Count, Q, Sum
import monthdelta
import json
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import connection
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.text import slugify
from django.utils.timezone import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import DeleteView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic import DetailView, FormView

from django_ajax.mixin import AJAXMixin
from braces.views import StaffuserRequiredMixin
from extra_views import CreateWithInlinesView, NamedFormsetsMixin, UpdateWithInlinesView
from haystack.query import RelatedSearchQuerySet
from haystack.views import SearchView
from rest_framework import status, views, serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from artists.models import Artist
from events.models import get_today_start, StaffPick, EventSet,\
    Recording, Comment
from events.serializers import MonthMetricsSerializer
from metrics.models import UserVideoMetric
from oscar_apps.catalogue.models import Product
from search.utils import facets_by_model_name
from .forms import EventAddForm, GigPlayedAddInlineFormSet, \
    GigPlayedInlineFormSetHelper, GigPlayedEditInlineFormset, \
    EventSearchForm, EventEditForm, EventSetInlineFormset, \
    EventSetInlineFormsetHelper, CommentForm
from .models import Event, Venue

RANGE_YEAR = 'year'
RANGE_MONTH = 'month'
RANGE_WEEK = 'week'

def get_weekly_range():
    now = timezone.now()
    range_start = (now - datetime.timedelta(days=now.weekday())).date()
    range_end = range_start + datetime.timedelta(weeks=1)
    return range_start, range_end


def get_monthly_range():
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    range_start = datetime.date(current_year, current_month, 1)
    range_end = datetime.date(
        current_year, current_month, calendar.monthrange(
            current_year, current_month
        )[1]
    )

    return range_start, range_end


def get_year_range():
    now = timezone.now()
    current_year = now.year

    range_start = datetime.date(current_year, 1, 1)
    range_end = datetime.date(current_year, 12, 31)

    return range_start, range_end


def calculate_query_range(range_size, weekly=None):
    range_start = None
    range_end = None
    if range_size:
        if range_size == RANGE_WEEK:
            range_start, range_end = get_weekly_range()
        elif range_size == RANGE_MONTH:
            range_start, range_end = get_monthly_range()
        elif range_size == RANGE_YEAR:
            range_start, range_end = get_year_range()

    else:
        if weekly:
            range_start, range_end = get_weekly_range()

    return range_start, range_end


@cached(timeout=6*60*60)
def _get_most_popular(range=None):
    context = {}
    most_popular_ids = UserVideoMetric.objects.most_popular(
        range_size=range, count=10
    )
    most_popular = []
    for event_data in most_popular_ids:
        try:
            event = Event.objects.get(id=event_data['event_id'])
            most_popular.append(event)
        except Event.DoesNotExist:
            pass
    context['popular_in_archive'] = most_popular
    return context


@cached(timeout=6*60*60)
def _get_most_popular_uploaded(range_size=None):
    range_start, range_end = calculate_query_range(range_size)

    sqs = Event.objects.filter(
        recordings__media_file__isnull=False,
        recordings__state=Recording.STATUS.Published
    )

    if range_start and range_end:
        sqs = sqs.filter(date__range=(range_start, range_end))

    return order_events_by_popular(sqs)


def order_events_by_popular(sqs):
    event_map = dict([(event.id, event) for event in sqs])
    # Order metrics
    most_popular_ids = UserVideoMetric.objects.filter(
        event_id__in=event_map.keys()
    ).values('event_id').annotate(
        count=Sum('seconds_played')
    ).order_by('-count')[:10]
    if most_popular_ids:
        most_popular = []
        for event_data in most_popular_ids:
            event_id = event_data['event_id']
            most_popular.append(event_map[event_id])

        return most_popular
    else:
        return list(sqs.order_by('-date')[:10])


def get_today_events():
    date_range_start = get_today_start()
    date_range_end = date_range_start + timedelta(days=1)
    qs = Event.objects.filter(start__gte=date_range_start,
                              start__lte=date_range_end)
    qs = qs.order_by('start')
    return qs


class HomepageView(ListView):
    template_name = 'home_new.html'
    context_object_name = 'events_today'

    def get_queryset(self):
        qs = get_today_events()
        # Uncomment to filter todays events by venue
        # venue = self.request.GET.get('venue')
        # if venue is not None:
        #     qs = qs.filter(venue__id=int(venue))

        return qs

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

        venue = self.request.GET.get('venue')
        if venue is not None:
            venue_id = int(venue)
            events = events.filter(venue__id=venue_id)
            context['venue_selected'] = venue_id

        # 30 events should be enough to show next 7 days with events
        events = events[:30]
        dates = {}
        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)
        # next 7 days
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0])).items()[:7]
        most_recent = Event.objects.most_recent()[:20]
        if len(most_recent):
            context['new_in_archive'] = most_recent
        else:
            context['new_in_archive'] = Event.objects.exclude(
                state=Event.STATUS.Draft
            ).order_by('-start')[:20]

        context['next_7_days'] = sorted_dates
        context['venues'] = Venue.objects.all()
        month_popular = _get_most_popular_uploaded(RANGE_MONTH)
        if len(month_popular):
            context['popular_in_archive'] = month_popular
            context['popular_select'] = 'month'
        else:
            context['popular_in_archive'] = _get_most_popular_uploaded()
            context['popular_select'] = 'alltime'

        context['staff_picks'] = Event.objects.last_staff_picks()
        context['popular_in_store'] = Product.objects.filter(featured=True, product_class__slug='album')[:6]
        return context


homepage = HomepageView.as_view()


class OldHomeView(HomepageView):
    template_name = 'home.html'


old_home = OldHomeView.as_view()


class MostPopularEventsAjaxView(AJAXMixin, ListView):
    context_object_name = 'events'
    model = Event
    template_name = "events/event_row.html"

    def __init__(self, **kwargs):
        super(MostPopularEventsAjaxView, self).__init__()
        self.ajax_mandatory = False

    def get_context_data(self, **kwargs):
        # Need to provide secondary = True for the event card
        context = super(MostPopularEventsAjaxView, self).get_context_data(**kwargs)
        context['secondary'] = True
        return context

    def get_queryset(self):
        metrics_range = RANGE_WEEK
        received_range = self.request.GET.get('range', 'weekly')
        if received_range:
            if received_range == 'week':
                metrics_range = RANGE_WEEK
            if received_range == 'month':
                metrics_range = RANGE_MONTH
            if received_range == 'year':
                metrics_range = RANGE_YEAR
            if received_range == 'alltime':
                metrics_range = None

        most_popular = _get_most_popular_uploaded(metrics_range)
        return most_popular


event_popular_ajax = MostPopularEventsAjaxView.as_view()


class StyleGuideView(TemplateView):
    template_name = 'style_guide.html'


styleguide = StyleGuideView.as_view()


def check_staff_picked(event, is_staff_pick):
    if is_staff_pick:
        if not hasattr(event, 'staff_picked'):
            StaffPick.objects.create(event=event,
                                     date_picked=timezone.now())
    else:
        if hasattr(event, 'staff_picked'):
            event.staff_picked.delete()


class EventAddView(StaffuserRequiredMixin, NamedFormsetsMixin, CreateWithInlinesView):
    template_name = 'events/event_add.html'
    model = Event
    form_class = EventAddForm
    inlines = [GigPlayedAddInlineFormSet, EventSetInlineFormset]
    inlines_names = ['artists', 'sets']

    def get_context_data(self, **kwargs):
        context = super(EventAddView, self).get_context_data(**kwargs)
        context['artists'].helper = GigPlayedInlineFormSetHelper()
        context['sets'].helper = EventSetInlineFormsetHelper()
        context['show_times'] = json.dumps(settings.SHOW_TIMES)
        return context

    def post(self, request, *args, **kwargs):
        response = super(EventAddView, self).post(request, *args, **kwargs)
        check_staff_picked(self.object, self.request.POST.get('staff_pick', 'off') == 'on')
        return response



event_add = EventAddView.as_view()


class EventDetailView(DetailView):
    queryset = Event.objects.all().select_related('recording', 'recording__media_file')
    context_object_name = 'event'
    template_name = 'events/event_details_new.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        event = self.object
        performers = event.get_performers()

        context['performers'] = [performers[i:i + 4] for i in range(0, len(performers), 4)]
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID
        context['metrics_ping_interval'] = settings.PING_INTERVAL
        context['metrics_server_url'] = settings.METRICS_SERVER_URL
        context['metrics_signed_data'] = self._generate_metrics_data()
        if self.request.user.is_authenticated():
            context['user_token'] = Token.objects.get(user=self.request.user)
            user_is_artist = (
                self.request.user.is_artist and
                self.request.user.artist in event.performers.all()
            )
            user_is_staff = self.request.user.is_staff
            if user_is_artist or user_is_staff:
                context['count_metrics'] = False
            else:
                context['count_metrics'] = True

        context['related_videos'] = Event.objects.event_related_videos(event)

        if event.is_today:
            context['streaming_tonight_videos'] = get_today_events()
            live_set = event.is_live
            if live_set:
                next_event_ids = get_today_events().values_list('id', flat=True)
                next_set = EventSet.objects.filter(
                    event_id__in=next_event_ids, start__gt=live_set.end
                ).first()

                if next_set:
                    context['next_streaming'] = {
                        'event_url': next_set.event.get_absolute_url(),
                        'start': live_set.utc_end + timedelta(minutes=2)
                    }

            else:
                first_set = event.sets.order_by('start').first()
                if first_set:
                    context['next_streaming'] = {
                        'event_url': event.get_absolute_url(),
                        'start': first_set.utc_start - timedelta(minutes=15)
                    }

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
    inlines = [GigPlayedEditInlineFormset, EventSetInlineFormset]
    inlines_names = ['artists', 'sets']

    def get_context_data(self, **kwargs):
        context = super(EventEditView, self).get_context_data(**kwargs)
        context['artists'].helper = GigPlayedInlineFormSetHelper()
        if 'sets' in context:
            context['sets'].helper = EventSetInlineFormsetHelper()
        context['show_times'] = json.dumps(settings.SHOW_TIMES)
        return context

    def get_form(self, form_class):
        form = super(EventEditView, self).get_form(form_class)
        if hasattr(self.object, 'staff_picked'):
            form.initial['staff_pick'] = True

        return form

    def post(self, *args, **kwargs):
        response = super(EventEditView, self).post(*args, **kwargs)
        check_staff_picked(self.object, self.request.POST.get('staff_pick', 'off') == 'on')
        return response


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

def annotate_events(events):
    return events.annotate(product_count=Count('products')).extra(select={
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


class GenericScheduleView(ListView):
    context_object_name = 'dates'
    template_name = 'events/schedule.html'

    def get_queryset(self):
        dates = {}
        date_range_end, date_range_start, number_of_days = self.get_dates_interval()
        self.date_start = date_range_start

        events = Event.objects.select_related(
            'venue'
        ).filter(
            start__range=(date_range_start, date_range_end)).order_by('start')

        if not self.request.user.is_staff:
            events = events.exclude(state=Event.STATUS.Draft)

        venue = self.request.GET.get('venue')
        if venue is not None:
            events = events.filter(venue__id=int(venue))

        events = annotate_events(events)

        for k, g in groupby(events, lambda e: e.listing_date()):
            dates[k] = list(g)

        for date in [
            (date_range_start + timedelta(days=days_after)).date()
            for days_after in range(number_of_days)
        ]:
            if date not in dates:
                dates[date] = []

        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0]))
        return sorted_dates

    def add_venue_next_prev(self, context, next_url, params_next, prev_url,
                            params_prev):
        venue = self.request.GET.get('venue')
        context['venues'] = Venue.objects.all()
        if venue is not None:
            venue_id = int(venue)
            context['venue_selected'] = venue_id
            params_next['venue'] = venue_id
            params_prev['venue'] = venue_id

        if prev_url and len(params_prev):
            prev_url = '{}?{}'.format(prev_url, urlencode(params_prev))
        if next_url and len(params_next):
            next_url = '{}?{}'.format(next_url, urlencode(params_next))
        context['prev_url'] = prev_url
        context['next_url'] = next_url

    def get_dates_interval(self):
        raise NotImplementedError()


class WeeklyScheduleView(GenericScheduleView):
    def get_dates_interval(self):
        received_week = int(self.request.GET.get('week', 0))
        number_of_days = 7
        # Range from now to
        date_range_start = (
            timezone.localtime(timezone.now()) +
            timezone.timedelta(days=(received_week * 7))
        )
        # don't show last nights events that are technically today
        date_range_start = date_range_start.replace(hour=10)
        # Set end one week later
        date_range_end = (
            date_range_start +
            timezone.timedelta(days=number_of_days)
        )
        return date_range_end, date_range_start, number_of_days

    def get_context_data(self, **kwargs):
        context = super(WeeklyScheduleView, self).get_context_data(**kwargs)
        context['events_today'] = get_today_events()

        context['month'] = self.date_start.month - 1
        context['year'] = self.date_start.year
        context['day'] = self.date_start.day

        base_url = reverse('schedule')
        params_next = {}
        params_prev = {}

        week = int(self.request.GET.get('week', 0))

        if week != 1:
            params_prev['week'] = week - 1

        if week != -1:
            params_next['week'] = week + 1

        prev_url = None
        if week:
            prev_url = base_url
        next_url = base_url

        self.add_venue_next_prev(
            context, next_url, params_next, prev_url, params_prev
        )

        return context


schedule = WeeklyScheduleView.as_view()


class MonthlyScheduleView(GenericScheduleView):
    def get_dates_interval(self):
        month = int(self.kwargs.get('month', timezone.now().month))
        year = int(self.kwargs.get('year', timezone.now().year))
        received_day = self.kwargs.get('day')

        day = 1
        if received_day:
            day = int(received_day)

        # don't show last nights events that are technically today
        date_range_start = timezone.make_aware(
            timezone.datetime(year, month, day, hour=10),
            timezone.get_default_timezone()
        )

        if not received_day:
            number_of_days = calendar.monthrange(year, month)[1]
            date_range_end = date_range_start + monthdelta.MonthDelta(1)
        else:
            number_of_days = 7
            date_range_end = date_range_start + timedelta(days=number_of_days)

        return date_range_end, date_range_start, number_of_days

    def get_context_data(self, **kwargs):
        """
        Timedelta doesn't support months so to get the next and previous months, we do a max delta (31 days) for the
        next month, and a min one (1 day) for the previous month.
        """
        context = super(MonthlyScheduleView, self).get_context_data(**kwargs)
        context['events_today'] = get_today_events()

        month = self.date_start.month
        year = self.date_start.year
        day = self.date_start.day

        context['month'] = month - 1
        context['year'] = year
        context['day'] = day
        context['month_view'] = True

        # position of the "NEXT" box, after all the dates and the "PREV" box
        context['next_month_position'] = len(context['dates']) + 2
        current_date = timezone.datetime(year=year, month=month, day=day)

        next_day = current_date + timezone.timedelta(days=7)
        prev_day = current_date - timezone.timedelta(days=7)

        prev_url = None
        if current_date.date() > timezone.now().date():
            prev_url = reverse('monthly_schedule',
                               kwargs={'year': prev_day.year,
                                       'month': prev_day.month,
                                       'day': prev_day.day})

        next_url = reverse('monthly_schedule',
                           kwargs={'year': next_day.year,
                                   'month': next_day.month,
                                   'day': next_day.day})

        self.add_venue_next_prev(
            context, next_url, {}, prev_url, {}
        )

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
        events = Event.objects.exclude(recordings=None)
        self.date_start = timezone.now()
        if dates:
            date_range_start = datetime.combine(dates[-1], std_time(10, 0))
            self.date_start = date_range_start
            date_range_end = dates[0] + timedelta(days=1)
            date_range_end = datetime.combine(date_range_end, std_time(4, 0))
            events = events.filter(start__gte=date_range_start, start__lte=date_range_end).order_by('start')

        venue = self.request.GET.get('venue')
        if venue is not None:
            events = events.filter(venue__id=int(venue))

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

            weekly_most_popular_ids = UserVideoMetric.objects.most_popular(
                weekly=False)
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

        venue = self.request.GET.get('venue')
        if venue is not None:
            venue_id = int(venue)
            context['venue_selected'] = venue_id

        context['venues'] = Venue.objects.all()
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


class PublishSet(GenericViewSet):
    queryset = EventSet.objects.all()

    def post(self, request, *args, **kwargs):
        event_set = self.get_object()

        try:
            recording = event_set.video_recording
            recording.state = Recording.STATUS.Published
            recording.save()

            recording = event_set.audio_recording
            recording.state = Recording.STATUS.Published
            recording.save()

        except Recording.DoesNotExist:
            pass

        return Response()


publish_set = PublishSet.as_view({'post': 'post'})


class MakePrivate(GenericViewSet):
    queryset = EventSet.objects.all()

    def post(self, request, *args, **kwargs):
        event_set = self.get_object()
        try:
            recording = event_set.video_recording
            recording.state = Recording.STATUS.Hidden
            recording.save()
            recording = event_set.audio_recording
            recording.state = Recording.STATUS.Hidden
            recording.save()
        except Recording.DoesNotExist:
            pass

        return Response()


make_private = MakePrivate.as_view({'post': 'post'})


# TODO Maybe include this "serialization" in metrics package?
class SessionEventsCountView(views.APIView):
    def get(self, request, format=None):
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        set_id = request.query_params.get('set_id')
        if set_id:
            metric_filter = Q(recording_id=set_id)
        else:
            event_ids = list(self.request.user.artist.gigs_played.values_list('event_id', flat=True))
            set_ids = list(Recording.objects.filter(event_id__in=event_ids).values_list('id', flat=True))
            metric_filter = Q(recording_id__in=set_ids)

        if start and end:
            try:
                start = serializers.DateField().to_internal_value(start)
                end = serializers.DateField().to_internal_value(end)
                metric_filter &= Q(date__range=(start, end))
            except TypeError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        counts = list(UserVideoMetric.objects.filter(metric_filter).values(
            'date', 'recording_type'
        ).order_by('date').total_counts_annotate().filter(seconds_played__gt=0))

        if not start or not end:
            if len(counts):
                start = counts[0]['date'] - timedelta(days=1)
                end = counts[-1]['date'] + timedelta(days=1)

        if start and end:
            days_in_range = (end - start).days + 1
            days = range(0, days_in_range)

            audio_play_counts = {}
            audio_minutes_counts = {}
            video_play_counts = {}
            video_minutes_counts = {}
            for entry in counts:
                day = (entry['date'] - start).days
                if entry['recording_type'] == 'V':
                    video_play_counts[day] = entry['play_count']
                    video_minutes_counts[day] = entry['seconds_played'] / 60
                else:
                    audio_play_counts[day] = entry['play_count']
                    audio_minutes_counts[day] = entry['seconds_played'] / 60

            audio_minutes_list = [audio_minutes_counts.get(day_number, 0) for day_number in days]
            video_minutes_list = [video_minutes_counts.get(day_number, 0) for day_number in days]
            count_data = dict(
                total_minutes_list=[a + v for a, v in zip(audio_minutes_list, video_minutes_list)]
            )

            count_data['dates'] = []
            for day in days:
                current_day = start + timedelta(day)
                count_data['dates'].append(current_day)
        else:
            count_data = dict(
                total_minutes_list=[],
                dates=[]
            )

        s = MonthMetricsSerializer()
        return Response(data=s.to_representation(count_data))

metrics_event_counts = SessionEventsCountView.as_view()


class CommentListView(FormView):

    form_class = CommentForm
    template_name = 'events/comments.html'

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404()
        return super(CommentListView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.get_full_path()

    def get_form_kwargs(self):
        kwargs = super(CommentListView, self).get_form_kwargs()
        initial = kwargs.get('initial', {})
        initial.update({
            'event_set': EventSet.objects.filter(
                event_id=self.kwargs.get('pk')
            ).first().id})
        kwargs['initial'] = initial
        return kwargs

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.save()
        return super(CommentListView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CommentListView, self).get_context_data(**kwargs)
        context['object_list'] = Comment.objects.filter(
            event_set__event_id=self.kwargs.get('pk'))
        return context

event_comments = CommentListView.as_view()
