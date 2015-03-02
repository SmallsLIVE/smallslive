import json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic import TemplateView

from django_ajax.mixin import AJAXMixin
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin, UserPassesTestMixin
from extra_views import CreateWithInlinesView, NamedFormsetsMixin, UpdateWithInlinesView
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from haystack.views import SearchView

from artists.models import Artist, Instrument
from .forms import EventAddForm, GigPlayedAddInlineFormSet, GigPlayedInlineFormSetHelper, GigPlayedEditInlineFormset, \
    EventSearchForm
from .models import Event
from multimedia.models import Media


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
    template_name = 'events/event_detail.html'

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

        facet_counts = super(EventSearchView, self).get_results().facet('model', order='term').facet_counts()
        fields = facet_counts.get('fields', {})
        facet_counts = {model: count for (model, count) in fields.get('model', [])}
        context.update({
            'artist_count': facet_counts.get('artist', 0),
            'event_count': facet_counts.get('event', 0),
            'instrument_count': facet_counts.get('instrument', 0),
        })

        artist_id = self.request.GET.get('artist')
        if artist_id:
            search_term = Artist.objects.get(id=artist_id).full_name()
        else:
            search_term = self.request.GET.get('q')
        context['search_term'] = search_term

        return context

    def get_results(self):
        return super(EventSearchView, self).get_results().models(Event).order_by('-start')

event_search = EventSearchView(
    form_class=EventSearchForm,
    searchqueryset=RelatedSearchQuerySet()
)


class ScheduleView(ListView):
    context_object_name = 'events'
    template_name = 'events/schedule.html'

    def get_queryset(self):
        """
        The view returns a list of events in two week intervals, for both the home page
        and the "next" links. The correct two week interval is set through the URL or by
        default it's a two week interval from the current date. The admin user sees all future
        events immediately, regardless of date intervals and event status.
        """
        two_week_interval = int(self.request.GET.get('week', 0))
        start_days = two_week_interval * 14
        date_range_start = timezone.localtime(timezone.now()) + timezone.timedelta(days=start_days)
        # don't show last nights events that are technically today
        date_range_start = date_range_start.replace(hour=10)
        date_range_end = date_range_start + timezone.timedelta(days=14)
        events = Event.objects.filter(start__gte=date_range_start, start__lte=date_range_end)
        # only admin sees draft and hidden events
        #events = events.filter(Q(state=Event.STATUS.Published) | Q(state=Event.STATUS.Cancelled))
        return events.reverse()

    def get_context_data(self, **kwargs):
        data = super(ScheduleView, self).get_context_data(**kwargs)
        week = int(self.request.GET.get('week', 0))
        if week > 1:
            data['prev_url'] = "{0}?week={1}".format(reverse('schedule'), week-1)
        elif week == 1:
            data['prev_url'] = reverse('schedule')
        # check if there are events in the next interval before showing the "next" link
        start_days = ((week + 1) * 14) + 1
        date_range_start = timezone.now().date() + timezone.timedelta(days=start_days)
        end_days = ((week + 2) * 14) + 1
        date_range_end = date_range_start + timezone.timedelta(days=end_days)
        next_events_exist = Event.objects.filter(start__range=(date_range_start, date_range_end)).exists()
        if next_events_exist:
            data['next_url'] = "{0}?week={1}".format(reverse('schedule'), week+1)
        return data

schedule = ScheduleView.as_view()


class EventCarouselAjaxView(AJAXMixin, ListView):
    context_object_name = 'events'

    def get_template_names(self):
        if self.request.GET.get("template") == "home":
            return ["blocks/homepage-upcoming-events-carousel.html"]
        else:
            return ["blocks/schedule-event-details-carousel.html"]

    def get_queryset(self):
        date = self.request.GET.get('date')
        print date
        if date and date != "undefined":
            date = datetime.strptime(date, "%m/%d/%Y").date()
            end_range_date = date + timedelta(days=1)
            return Event.objects.filter(start__range=(date, end_range_date)).order_by('start')
        return Event.objects.none()

event_carousel_ajax = EventCarouselAjaxView.as_view()