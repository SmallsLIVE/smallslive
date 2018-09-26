import json
from collections import OrderedDict
from itertools import chain, groupby

from dateutil import parser
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponse, JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import timedelta
from django.views.generic import View
from django.views.generic.base import TemplateView
from haystack.query import SearchQuerySet

from artists.models import Artist, Instrument
from events.models import Event, Venue

from .search import SearchObject
from .utils import facets_by_model_name


def search_autocomplete(request):
    sqs = SearchQuerySet().autocomplete(content=request.GET.get('term', '')).facet('model')
    artists = sqs.filter(model_exact="artist").load_all()[:5]
    events = sqs.filter(model_exact="event").order_by('-start').load_all()[:5]
    instruments = sqs.filter(model_exact="instrument").load_all()[:5]
    suggestions = [{'label': result.object.autocomplete_label(),
                    'sublabel': result.object.autocomplete_sublabel(),
                    'category': result.model_exact,
                    'url': result.object.get_absolute_url()} for result in chain(artists, events, instruments) if result]

    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps({
        'counts': facets_by_model_name(sqs),
        'results': suggestions,
    }, sort_keys=True)
    resp = HttpResponse(the_data, content_type='application/json')
    return resp


class SearchMixin(object):

    def search(self, entity, main_search, page=1, order=None,
               instrument=None, date_from=None, date_to=None, artist_search=None, artist_pk=None):

        search = SearchObject()

        if entity == Artist:
            results_per_page = 32
            sqs = search.search_artist(main_search, artist_search, instrument)

        elif entity == Event:
            results_per_page = 24
            sqs = search.search_event(main_search, order, date_from, date_to, artist_pk=artist_pk)

        blocks = []
        block = []

        paginator = Paginator(sqs, results_per_page)

        try:
            objects = paginator.page(page).object_list
        except EmptyPage:
            objects = []

        for item in objects:
            object_item = entity.objects.filter(pk=item.pk).first()
            block.append(object_item)

            if len(block) == 8 and entity == Artist:
                blocks.append(block)
                block = []

        if block:
            blocks.append(block)
            block = []

        if paginator.count:
            actual_results = 1 + ((page - 1) * results_per_page) if entity == Artist else 1
            showing_results = 'SHOWING {} - {} OF {} RESULTS'.format(actual_results,
                results_per_page + ((page - 1) * results_per_page) if page != paginator.num_pages else len(
                    paginator.page(page).object_list) + ((page - 1) * results_per_page),
                paginator.count)
        else:
            showing_results = 'NO RESULTS'

        return blocks, showing_results, paginator.num_pages


class UpcomingEventMixin(object):

    def get_upcoming_events_context_data(self, context):
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
        sorted_dates = OrderedDict(sorted(dates.items(), key=lambda d: d[0])).items()[:7]
        context['next_7_days'] = sorted_dates
        most_recent = Event.objects.most_recent()[:20]
        if len(most_recent):
            context['new_in_archive'] = most_recent
        else:
            context['new_in_archive'] = Event.objects.exclude(
                state=Event.STATUS.Draft
            ).order_by('-start')[:20]
        context['venues'] = Venue.objects.all()
        return context


class MainSearchView(View, SearchMixin):

    def get(self, request, *args, **kwargs):
        main_search = request.GET.get('main_search', None)
        artist_search = request.GET.get('artist_search', None)
        page = int(request.GET.get('page', 1))
        entity = self.kwargs.get('entity', None)
        order = request.GET.get('order', None)
        instrument = request.GET.get('instrument', None)
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)
        artist_pk = request.GET.get('artist_pk', None)

        if date_from:
            date_from = parser.parse(date_from, fuzzy=True)
        if date_to:
            date_to = parser.parse(date_to, fuzzy=True)

        if entity == 'artist':
            artists_blocks, showing_results, num_pages = self.search(
                Artist, main_search, page, instrument=instrument, artist_search=artist_search)

            context = {'artists_blocks': artists_blocks}
            template = 'search/artist_results.html'

        elif entity == 'event':
            events, showing_results, num_pages = self.search(
                Event, main_search, page, order=order, date_from=date_from, date_to=date_to, artist_pk=artist_pk)

            context = {'events': events[0] if events else []}
            template = 'search/event_search_result.html'
        else:
            return Http404('entity does not exist')

        temp = render_to_string(template,
                                context,
                                context_instance=RequestContext(request)
                                )

        data = {
            'template': temp,
            'showingResults': showing_results,
            'numPages': num_pages
        }

        if entity == 'event':
            context = {'actual_page': page,
                       'last_page': num_pages,
                       'range': range(1, num_pages + 1)[:page][-3:] + range(1, num_pages + 1)[page:][:2],
                       'has_last_page': (num_pages - page) >= 3}
            template = 'search/page_numbers_footer.html'
            temp = render_to_string(template,
                                    context,
                                    context_instance=RequestContext(request)
                                    )

            data['pageNumbersFooter'] = temp

        return JsonResponse(data)


#
#   this is a proof of concept, once it is approved it will be refactored
#
class SearchBarView(View):

    def get(self, request, *args, **kwargs):
        main_search = request.GET.get('main_search', None)
        search = SearchObject()

        artists = []
        artist_results_per_page = 6
        sqs = search.search_artist(main_search)
        paginator = Paginator(sqs, artist_results_per_page)
        artists_results = paginator.count

        for item in paginator.page(1).object_list:
            item = Artist.objects.filter(pk=item.pk).first()
            artists.append(item)
        artists_results_left = artists_results - len(artists)
        
        events = []
        event_results_per_page = 8
        sqs = search.search_event(main_search)
        paginator = Paginator(sqs, event_results_per_page)
        events_results = paginator.count

        for item in paginator.page(1).object_list:
            item = Event.objects.filter(pk=item.pk).first()
            events.append(item)
        events_results_left = events_results - len(events)

        context = {'artists': artists,
                   'artists_results': artists_results,
                   'artists_results_left': artists_results_left,
                   'events': events,
                   'events_results': events_results,
                   'events_results_left': events_results_left}
        template = 'search/search_bar_results.html'

        temp = render_to_string(template,
                                context,
                                context_instance=RequestContext(request)
                                )

        data = {
            'template': temp
        }

        return JsonResponse(data)


class TemplateSearchView(TemplateView, SearchMixin, UpcomingEventMixin):
    template_name = 'search/search.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateSearchView, self).get_context_data(**kwargs)
        context = self.get_upcoming_events_context_data(context)
        q = self.request.GET.get('q', '')

        artists_blocks, showing_artist_results, num_pages = self.search(
            Artist, q)

        instruments = [i.name for i in Instrument.objects.all()]
        context['instruments'] = instruments

        context['showing_artist_results'] = showing_artist_results
        context['artists_blocks'] = artists_blocks
        context['artist_num_pages'] = num_pages

        event_blocks, showing_event_results, num_pages = self.search(Event, q)

        context['showing_event_results'] = showing_event_results
        context['event_results'] = event_blocks[0] if event_blocks else []

        context['actual_page'] = page = 1
        context['last_page'] = num_pages
        context['range'] = range(
            1, num_pages + 1)[:page][-3:] + range(1, num_pages + 1)[page:][:2]
        context['has_last_page'] = (num_pages - page) >= 3

        return context


class ArtistInfo(View):

    def get(self, request, *args, **kwargs):
        id = request.GET.get('id', None)

        artist = Artist.objects.filter(pk=id).first()

        context = {'artist': artist}
        template = 'artists/artist_detail_search.html'

        temp = render_to_string(template,
                                context,
                                context_instance=RequestContext(request)
                                )

        data = {
            'template': temp
        }

        return JsonResponse(data)
