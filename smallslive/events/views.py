import functools
from collections import OrderedDict
from itertools import groupby
import calendar
import datetime
from datetime import time as std_time
from dateutil.relativedelta import relativedelta
from cacheops import cached
from django.contrib import messages
from django.core import signing
from django.db.models import Count, F, Q, Sum
import monthdelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.db import connection
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.http.response import Http404
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import DeleteView, TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView
from django.views.generic import DetailView, FormView

# from django_ajax.mixin import AJAXMixin
from braces.views import StaffuserRequiredMixin
from extra_views import CreateWithInlinesView, NamedFormsetsMixin, UpdateWithInlinesView
from haystack.query import RelatedSearchQuerySet
from haystack.views import SearchView
from rest_framework import status, views, serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.contrib.sites.models import Site


from artists.models import Artist
from events.models import get_today_start, StaffPick, EventSet, \
    Recording, Comment
from metrics.models import UserVideoMetric
from oscar_apps.catalogue.models import Product
from search.views import SearchMixin, UpcomingEventMixin, UpcomingSearchView
from search.utils import facets_by_model_name
from .forms import EventAddForm, GigPlayedAddInlineFormSet, \
    GigPlayedInlineFormSetHelper, GigPlayedEditInlineFormset, \
    EventSearchForm, EventEditForm, EventSetInlineFormset, \
    EventSetInlineFormsetHelper, CommentForm, TicketAddForm, \
    ShowDefaultTimeInlineFormset, ShowDefaultTimeInlineFormsetHelper, \
    VenueAddForm
from .models import Event, Venue, ShowDefaultTime, RANGE_MONTH
from events.mixins import CurrentSiteIdMixin

RANGE_YEAR = 'year'
RANGE_MONTH = 'month'
RANGE_WEEK = 'week'


def get_weekly_range():
    now = timezone.now()
    last_week = now - relativedelta(weeks=1)
    range_start = (now - datetime.timedelta(days=now.weekday())).date()
    range_end = range_start + datetime.timedelta(weeks=1)

    return last_week.replace(hour=0, minute=0, second=0), now

    # return range_start, range_end


def get_monthly_range():

    now = timezone.now()
    last_month = now - relativedelta(months=1)

    current_year = now.year
    current_month = last_month.month

    range_start = datetime.date(current_year, current_month, 1)
    range_end = datetime.date(
        current_year, current_month, calendar.monthrange(
            current_year, current_month
        )[1]
    )

    return last_month.replace(hour=0, minute=0, second=0), now

    # return range_start, range_end


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

       
class HomepageView(ListView, UpcomingEventMixin, CurrentSiteIdMixin):
    template_name = 'home_new.html'

    def get_queryset(self):
        return Event.objects.get_today_and_tomorrow_events(
            just_today=True, is_staff=self.request.user.is_staff)

    def get_today_events(self):
        events = list(self.get_queryset())
        return [x for x in events if not x.is_past]

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        
        context = self.get_site_context_data(context)
        context = self.get_upcoming_events_context_data(context)

        if self.request.user.is_authenticated:
            a = datetime.datetime.strftime(self.request.user.date_joined, '%Y-%m-%d')
            b = datetime.datetime.strftime(timezone.now(), '%Y-%m-%d')
            context['email_sent'] = a == b

        context['staff_picks'] = Event.objects.last_staff_picks()
        context['popular_in_store'] = Product.objects.filter(featured=True, product_class__slug='album')[:6]
        context['popular_in_archive'] = Event.objects.get_most_popular_uploaded()
        context['popular_select'] = 'alltime'
        context['events_today'] = list(self.get_queryset())
        #context['SITE_ID'] = settings.SITE_ID

        activation_key =  self.request.GET.get('activate_account')
        if activation_key:
            context['activation_key'] = activation_key

        most_recent = Event.objects.recently_added()[:20]
        if len(most_recent):
            context['new_in_archive'] = most_recent
        else:
            context['new_in_archive'] = Event.objects.exclude(
                state=Event.STATUS.Draft
            ).order_by('-start')[:20]

        return context


homepage = HomepageView.as_view()

class RederictToHome(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('home'))

redirect_to_home = RederictToHome.as_view()

class OldHomeView(HomepageView):
    template_name = 'home.html'


old_home = OldHomeView.as_view()


class MostPopularEventsAjaxView(ListView):
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
        # Class needed in template to identify the carousel (owl carousel).
        context['carousel'] = 'popular-carousel'
        return context

    def get_queryset(self):
        metrics_range = RANGE_WEEK
        received_range = self.request.GET.get('range', 'week')
        if received_range and received_range in ['week', 'month', 'year']:
            if received_range == 'week':
                metrics_range = RANGE_WEEK
            if received_range == 'month':
                metrics_range = RANGE_MONTH
            if received_range == 'year':
                metrics_range = RANGE_YEAR

            most_popular = Event.objects.get_most_popular_uploaded(range_size=metrics_range)
        else:
            most_popular = Event.objects.get_most_popular_uploaded()

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


TICKETS_NUMBER_OF_SETS = 4


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
        default_sets = []
        for default_set in ShowDefaultTime.objects.all():
            default_sets.append({
                'set-venue':
                    str(default_set.get_venue_name()),
                'set-starts': default_set.sets_start(),
                'set-redeable-starts': default_set.sets_readable_start(),
                'set-duration': default_set.set_duration,
                'set-title': str(default_set.title),
            })
        context['show_times'] = default_sets
        context['ticket_forms'] = self.construct_ticket_forms()

        return context

    def forms_valid(self, form, inlines):
        response = super(EventAddView, self).forms_valid(form, inlines)

        check_staff_picked(self.object, self.request.POST.get('staff_pick', 'off') == 'on')
        ticket_forms = self.construct_ticket_forms(data=self.request.POST)
        event_sets = self.object.sets.all()
        event_sets = sorted(event_sets, key=functools.cmp_to_key(Event.sets_order))
        count = 0
        for event_set in event_sets:
            ticket_form = ticket_forms[count]
            count += 1
            if ticket_form.is_valid():
                if ticket_form.cleaned_data.get('form_enabled'):
                    ticket_form.save(event_set=event_set)

        return response

    def forms_invalid(self, form, inlines):
        response = super(EventAddView, self).forms_invalid(form, inlines)
        return response

    def construct_ticket_forms(self, data=None):
        ticket_forms = []
        for i in range(1, TICKETS_NUMBER_OF_SETS + 1):
            ticket_form = TicketAddForm(data, prefix="set{0}".format(i), number=i)
            ticket_forms.append(ticket_form)
        return ticket_forms


event_add = EventAddView.as_view()


class EventDetailView(DetailView):
    queryset = Event.objects.all()
    context_object_name = 'event'

    def get(self, request, *args, **kwargs):

        result = super(EventDetailView, self).get(request, *args, **kwargs)
        if self.object.state != Event.STATUS.Published:
            if not self.request.user.is_authenticated or not self.request.user.is_staff:
                return HttpResponseRedirect(reverse('home'))

        return result

    def get_context_data(self, **kwargs):
        current_user = self.request.user
        context = super(EventDetailView, self).get_context_data(**kwargs)
        event = self.object
        performers = event.get_performers()
        self.request.is_event = True
        context['comma_separated_artists'] = event.get_performer_strings()
        context['performers'] = [performers[i:i + 4] for i in range(0, len(performers), 4)]
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID
        context['metrics_ping_interval'] = settings.PING_INTERVAL
        context['metrics_signed_data'] = self._generate_metrics_data()
        context['event_metrics_update_url'] = reverse('event_update_metrics', kwargs={'pk': event.pk})
        # In case the user selects a ticket
        context['flow_type'] = "ticket_selection"
        if self.request.user.is_authenticated:
            context['user_token'] = Token.objects.get(user=self.request.user)
            user_is_artist = (
                current_user.is_artist and
                current_user.artist in event.performers.all()
            )
            if user_is_artist or current_user.is_staff or not current_user.has_activated_account:
                context['count_metrics'] = False
            else:
                context['count_metrics'] = True

        context['related_videos'] = Event.objects.event_related_videos(event)
        events = Event.objects.get_today_and_tomorrow_events(
            just_today=True, is_staff=self.request.user.is_staff)
        context['streaming_tonight_videos'] = events

        # In this case, we need to change show info without reloading
        # The strategy is to provide the next show's info as hidden elements
        # They will be swapped with current info at start time.

        if event.show_streaming:
            next_event = event.get_next_event(is_staff=self.request.user.is_staff)
            if next_event:
                title = next_event.title
                date = next_event.date
                sets_info = next_event.get_sets_info_dict()
                artists_info = next_event.get_artists_info_dict()
                start = next_event.get_actual_start_end()[0] - timedelta(
                    minutes=next_event.start_streaming_before_minutes)

                context['next_event'] = {
                    'title': title,
                    'date': date,
                    'sets_info': sets_info,
                    'artists_info': artists_info,
                    'start': start
                }

        live_events = None
        if event.is_future or event.is_past:
            live_events = Event.objects.get_live(event.venue_id)
            if live_events:
                context['currently_live_event_url'] = live_events[0].get_absolute_url()

        if event.is_future or event.is_live:
            event_url = event.get_absolute_url()
            start = event.get_actual_start_end()[0] - timedelta(
                minutes=event.start_streaming_before_minutes)

            context['streaming'] = {
                'event_url': event_url,
                'start': start
            }
            context['products'] = self.object.get_tickets()

        # for modal in past events
        # need to find if there is currently a live event
        if live_events:
            context['finished_next_event'] = live_events[0]

        context['archived_date_estimate'] = self.object.end + timedelta(days=14)

        context['sets'] = event.get_sets_info_dict()
        context['event_artists'] = event.get_artists_info_dict()
        context['donate_url'] = reverse('donate')
        context['current_user'] = self.request.user
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY

        if event.venue.get_stripe_publishable_key:
            context['STRIPE_PUBLIC_KEY'] = event.venue.get_stripe_publishable_key

        return context

    def get_template_names(self):
        event = self.object

        if event.show_streaming:
            if self.request.user.is_authenticated:
                return ['events/_event_details_streaming.html']
            else:
                return ['events/_event_details_upcoming.html']
        elif event.is_past:
            return ['events/_event_details_past.html']
        if event.is_future or not event.streamable:
            return ['events/_event_details_upcoming.html']
        else:  # Not sure if there will be another option.
            if self.request.user.is_authenticated:
                return ['events/_event_details_streaming.html']
            else:
                return ['events/_event_details_upcoming.html']

    def _generate_metrics_data(self):
        data = {}
        for rec in self.object.recordings.all():
            rec_data = {
                'recording_id': rec.id,
                'recording_type': rec.media_file.media_type.upper()[0],
                'event_id': self.object.id,
                'event_date': self.object.start.strftime('%Y-%m-%dT%H:%M:%S'),
                'user_id': self.request.user.id,
            }
            signed_value = signing.dumps(rec_data)
            data[rec.id] = signed_value
        return data


event_detail = EventDetailView.as_view()


class EventDetailRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):

        original_id = kwargs.get('pk')
        event = Event.objects.get(original_id=original_id)
        self.url = event.get_absolute_url()

        return super(EventDetailRedirectView, self).get_redirect_url(*args, **kwargs)


event_detail_redirect = EventDetailRedirectView.as_view()


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
        default_sets = []
        for default_set in ShowDefaultTime.objects.all():
            default_sets.append({"set-venue" : str(default_set.get_venue_name()), "set-starts": default_set.sets_start(), "set-redeable-starts":  default_set.sets_readable_start(), "set-duration": default_set.set_duration, "set-title": str(default_set.title)})
        context['show_times'] = default_sets
        context['ticket_forms'] = self.construct_ticket_forms()

        return context

    def get_form(self, form_class):
        form = super(EventEditView, self).get_form(form_class)
        if hasattr(self.object, 'staff_picked'):
            form.initial['staff_pick'] = True

        return form

    def post(self, *args, **kwargs):
        response = super(EventEditView, self).post(*args, **kwargs)
        check_staff_picked(self.object, self.request.POST.get('staff_pick', 'off') == 'on')
        ticket_forms = self.construct_ticket_forms(data=self.request.POST)

        event_sets = self.object.sets.all()
        event_sets = sorted(event_sets, key=functools.cmp_to_key(Event.sets_order))
        count = 0
        for event_set in event_sets:
            # Ignore creating a ticket for the set if there's one already
            if event_set.tickets.count():
                continue
            ticket_form = ticket_forms[count]
            count += 1
            if ticket_form.is_valid():
                if ticket_form.cleaned_data.get('form_enabled'):
                    ticket_form.save(event_set=event_set)

        return response

    # TODO: remove duplicate code
    def construct_ticket_forms(self, data=None):
        ticket_forms = []
        event_sets = self.object.sets.all()
        for i, event_set in enumerate(event_sets):
            # Do not show a form if the set is already linked to a ticket.
            # Tickets can be created also from the store dashboard.
            if self.object.sets.filter(tickets__event_set=event_set):
                continue
            ticket_form = TicketAddForm(data,
                                        prefix='set{0}'.format(i + 1),
                                        number=i + 1,
                                        initial={'set_name': event_set.start.strftime('%-I:%M %p')})
            ticket_forms.append(ticket_form)

        return ticket_forms


event_edit = staff_member_required(EventEditView.as_view())


class EventDeleteView(StaffuserRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('home')


event_delete = EventDeleteView.as_view()


class EventCloneView(StaffuserRequiredMixin, DetailView):
    model = Event

    def __init__(self, *args, **kwargs):
        self.new_object = None
        self.object = None
        super(EventCloneView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        old_event_id = self.object.id
        gig_info = self.object.get_performers()
        event_sets = self.object.sets.all()
        new_object = self.object
        new_object.pk = None
        new_object.state = Event.STATUS.Draft
        new_object.seconds_played = 0
        new_object.play_count = 0
        new_object.original_id = None
        new_object.last_modify_by = None
        new_object.save()
        for info in gig_info:
            info.pk = None
            info.event = new_object
            info.save()
        for event_set in event_sets:
            event_set.pk = None
            event_set.event = new_object
            event_set.audio_recording = None
            event_set.video_recording = None
            event_set.save()

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


class EventUpdateMetricsView(View):

    def post(self, request, pk):

        event = Event.objects.get(pk=pk)
        event.update_metrics()

        return JsonResponse({'success': True})


event_update_metrics = EventUpdateMetricsView.as_view()


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


class GenericScheduleView(TemplateView, UpcomingSearchView, CurrentSiteIdMixin):
    context_object_name = 'dates'
    template_name = 'events/new_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(GenericScheduleView, self).get_context_data(**kwargs)
        context = self.get_site_context_data(context)
        context['venues'] = Venue.objects.all()
        context['default_from_date'] = timezone.now().strftime('%m/%d/%Y')
        context.update(self.get_upcoming_context())
        return context


schedule = GenericScheduleView.as_view()


class LivestreamView(TemplateView, UpcomingSearchView):
    template_name = 'basic_pages/livestream.html'

    def get_context_data(self, **kwargs):
        context = super(LivestreamView, self).get_context_data(**kwargs)
        context['site'] = Site.objects.get(id=2)
        return context


livestream = LivestreamView.as_view()


class TicketingView(TemplateView, UpcomingSearchView):
    template_name = 'basic_pages/ticketing.html'

    def get_context_data(self, **kwargs):
        context = super(TicketingView, self).get_context_data(**kwargs)

        return context


ticketing = TicketingView.as_view()


class FoundationView(TemplateView, UpcomingSearchView):
    template_name = 'basic_pages/foundation.html'

    def get_context_data(self, **kwargs):
        context = super(FoundationView, self).get_context_data(**kwargs)

        return context


foundation = FoundationView.as_view()


class StoreView(TemplateView, UpcomingSearchView):
    template_name = 'basic_pages/store.html'

    def get_context_data(self, **kwargs):
        context = super(StoreView, self).get_context_data(**kwargs)

        return context


store = StoreView.as_view()

class AboutView(TemplateView, UpcomingSearchView):
    if settings.SITE_ID == 1:
        template_name = 'basic_pages/about.html'
    elif settings.SITE_ID == 2:
        template_name = 'basic_pages/about_foundation.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        return context


about = AboutView.as_view()

class ContactView(TemplateView, UpcomingSearchView):
    template_name = 'basic_pages/contact.html'

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        return context


contact = ContactView.as_view()




class ScheduleCarouselAjaxView(DetailView):
    context_object_name = 'event'
    model = Event
    template_name = "blocks/schedule-event-details-carousel.html"


schedule_carousel_ajax = ScheduleCarouselAjaxView.as_view()


class HomepageEventCarouselAjaxView(ListView):
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

        @cached(timeout=6 * 60 * 60)
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


class PublishEvent(GenericViewSet):
    queryset = Event.objects.all()

    def post(self, request, *args, **kwargs):

        event = self.get_object()
        data = {'success': True}

        try:
            if event.has_published_media():
                for event_set in event.sets.with_media():
                    recording = event_set.video_recording
                    if recording:
                        recording.state = Recording.STATUS.Hidden
                        recording.save()

                    recording = event_set.audio_recording
                    if recording:
                        recording.state = Recording.STATUS.Hidden
                        recording.save()

                    data['is_published'] = False
            else:
                for event_set in event.sets.with_media():
                    recording = event_set.video_recording
                    if recording:
                        recording.state = Recording.STATUS.Published
                        recording.save()

                    recording = event_set.audio_recording
                    if recording:
                        recording.state = Recording.STATUS.Published
                        recording.save()
                    data['is_published'] = True

        except Recording.DoesNotExist:
            data['success'] = False
            data['message'] = 'Recording does not exist'

        return JsonResponse(data)

publish_event = PublishEvent.as_view({'post': 'post'})


# TODO Maybe include this "serialization" in metrics package?
class SessionEventsCountView(views.APIView):

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        set_id = request.query_params.get('set_id')

        if set_id:
            event_set = EventSet.objects.get(pk=set_id)
            audio_recording_id = event_set.audio_recording_id
            video_recording_id = event_set.video_recording_id

            metric_filter = Q(recording_id__in=[audio_recording_id,
                                                video_recording_id])
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

        qs = UserVideoMetric.objects.filter(metric_filter)

        qs = qs.values('event_id').annotate(play_count=Sum('play_count'))
        if qs.count():
            play_count = qs[0]['play_count']
        else:
            play_count = 0

        qs = UserVideoMetric.objects.filter(metric_filter)
        qs = qs.values('event_id').annotate(seconds_played=Sum('seconds_played'))
        if qs.count():
            seconds_played = qs[0]['seconds_played']
        else:
            seconds_played = 0

        data = {
            'playCount': play_count,
            'secondsPlayed': seconds_played,
        }

        return JsonResponse(data)


metrics_event_counts = SessionEventsCountView.as_view()


class CommentListView(FormView):

    form_class = CommentForm
    template_name = 'events/comments.html'

    def dispatch(self, request, *args, **kwargs):
        set_index = int(request.GET.get('set') or 0)
        self.event = Event.objects.get(id=kwargs.get('pk'))
        self.event_set = self.event.sets.all()[set_index]
        return super(CommentListView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.can_watch_video:
            raise Http404()
        return super(CommentListView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        url = self.request.build_absolute_uri()
        if 'https' not in url:
            url = url.replace('http', 'https')
        return url

    def get_form_kwargs(self):
        kwargs = super(CommentListView, self).get_form_kwargs()
        initial = kwargs.get('initial', {})
        initial.update({'event_set': self.event_set})
        kwargs['initial'] = initial
        return kwargs

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.save()
        if self.request.is_ajax():
            return JsonResponse({'success': True, 'url': self.get_success_url()})
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CommentListView, self).get_context_data(**kwargs)
        context['object_list'] = self.event_set.comments.all()
        return context


event_comments = CommentListView.as_view()


class VenueAddView(StaffuserRequiredMixin, NamedFormsetsMixin, CreateWithInlinesView):
    model = Venue
    form_class = VenueAddForm
    inlines = [ShowDefaultTimeInlineFormset]
    inlines_names = ['default_times']
    template_name = 'events/venue_add.html'

    def get_context_data(self, **kwargs):
        context = super(VenueAddView, self).get_context_data(**kwargs)
        context['default_times'].helper = ShowDefaultTimeInlineFormsetHelper()
        context['action_name'] = 'add'
        return context

    def get_success_url(self):
        return reverse('venue_edit', kwargs={'pk': self.object.id})

venue_add = VenueAddView.as_view()


class VenueEditView(StaffuserRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    model = Venue
    form_class = VenueAddForm
    inlines = [ShowDefaultTimeInlineFormset]
    inlines_names = ['default_times']
    template_name = 'events/venue_add.html'

    def get_context_data(self, **kwargs):
        context = super(VenueEditView, self).get_context_data(**kwargs)
        context['default_times'].helper = ShowDefaultTimeInlineFormsetHelper()
        context['action_name'] = 'edit'
        return context

    def get_success_url(self):
        return reverse('venue_edit', kwargs={'pk': self.object.id})

venue_edit = VenueEditView.as_view()


@login_required
def remove_comment(request):
    comment = Comment.objects.get(pk=request.POST.get('id'))
    success_url = comment.event_set.event.get_absolute_url()
    comment.delete()
    messages.info(request, "Comment deleted")
    return HttpResponseRedirect(success_url)


class MaintenanceView(TemplateView):

    template_name = 'maintenance.html'


maintenance_view = MaintenanceView.as_view()
