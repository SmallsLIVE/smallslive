import json
import string
from itertools import chain
import datetime
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
from events.models import Event, Venue, RANGE_MONTH

from .mixins import SearchMixin, UpcomingEventMixin
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


def artist_form_autocomplete(request):
    artist_start = request.GET.get('artist-start', None)
    artist_qs = Artist.objects.filter(first_name__istartswith=artist_start)
    artist_list = []
    for artist in artist_qs:
        artist_data = {'full_name' : artist.full_name(), 'val': artist.pk}
        artist_list.append(artist_data)
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    data = {
        'artist_list': artist_list
    }

    return JsonResponse(data)


class MainSearchView(View, SearchMixin):

    def get(self, request, *args, **kwargs):

        # TODO: Why
        main_search = request.GET.get('main_search', None)
        artist_search = request.GET.get('artist_search', None)
        page = int(request.GET.get('page', 1))
        entity = self.kwargs.get('entity', None)
        order = request.GET.get('order', None)
        leader = request.GET.get('leader', 'all')
        instrument = request.GET.get('instrument', None)
        artist_pk = request.GET.get('artist_pk', None)
        venue = request.GET.get('venue', None)
        partial = request.GET.get('partial', False)
        show_venue = request.GET.get('show_event_venue', False)
        show_sets = request.GET.get('show_event_setTime', False)
        upcoming = request.GET.get('is_upcoming', False)
        referer = request.META.get('HTTP_REFERER', '')

        date_from, date_to = self.get_filter_dates(referer)

        if entity == 'artist':

            artists_blocks, showing_results, num_pages, search_input = self.search(
                Artist, main_search, page, instrument=instrument, artist_search=artist_search)

            context = {
                'artists_blocks': artists_blocks,
                'query_term': main_search,
            }
            template = 'search/artist_results.html'

        elif entity == 'event':

            events, showing_results, num_pages, first, last, search_input = self.search(
                Event, main_search,
                page=page, order=order, date_from=date_from,
                date_to=date_to, artist_pk=artist_pk, venue=venue,
                instrument=instrument, artist_search=artist_search, leader=leader)

            context = {
                'events': events[0] if events else [],
                'secondary': True,
                'show_event_venue': show_venue,
                'show_extend_date': show_sets,
                'upcoming':  upcoming,
                'with_date_picker': True,
            }
            if self.request.user.is_staff:
                context['show_metrics'] = True

            template = ('search/event_search_row.html' if partial
                        else 'search/event_search_result.html')
        else:
            return Http404('entity does not exist')

        temp = render_to_string(
            template,
            context,
            context_instance=RequestContext(request)
        )

        data = {
            'template': temp,
            'showingResults': showing_results,
            'numPages': num_pages
        }

        return JsonResponse(data)


class SearchBarView(View):

    def get(self, request, *args, **kwargs):

        main_search = request.GET.get('main_search', None)
        search = SearchObject()
        search_input = search.process_input(main_search)
        terms, instruments, all_sax_instruments, partial_instruments, number_of_performers, \
            first_name, last_name, partial_name, artist_search = search_input

        artists = []
        artist_results_per_page = 6

        sqs = search.search_artist(terms, instruments, all_sax_instruments, partial_instruments,
                                   first_name, last_name, partial_name, artist_search)
        
        paginator = Paginator(sqs, artist_results_per_page)
        artists_results = paginator.count

        for item in paginator.page(1).object_list:
            item = Artist.objects.filter(pk=item.pk).first()
            artists.append(item)
        artists_results_left = artists_results - len(artists)
        
        events = []
        event_results_per_page = 8

        sqs = search.search_event(terms, instruments=instruments,
                                  all_sax_instruments=all_sax_instruments,
                                  first_name=first_name, last_name=last_name,
                                  partial_name=partial_name, artist_search=artist_search,
                                  number_of_performers=number_of_performers)

        paginator = Paginator(sqs, event_results_per_page)
        events_results = paginator.count

        for item in paginator.page(1).object_list:
            item = Event.objects.filter(pk=item.pk).first()
            events.append(item)
        events_results_left = events_results - len(events)

        if partial_instruments:
            partial_instruments = search.get_instrument(partial_instruments)
            partial_instruments = [x.name for x in partial_instruments]
            instruments += partial_instruments
        instruments_results = len(instruments)

        context = {'artists': artists,
                   'artists_results': artists_results,
                   'artists_results_left': artists_results_left,
                   'events': events,
                   'events_results': events_results,
                   'events_results_left': events_results_left,
                   'instruments': instruments,
                   'instruments_results': instruments_results}
        template = 'search/search_bar_results.html'

        temp = render_to_string(template,
                                context,
                                context_instance=RequestContext(request)
                                )

        data = {
            'template': temp
        }

        return JsonResponse(data)


class TemplateSearchView(SearchMixin, UpcomingEventMixin, TemplateView):

    template_name = 'search/search.html'

    def get_query_context(self):
        q = self.request.GET.get('q', '')

        return q, {}

    def get_artist_search_filter(self, referer):

        artist_search = self.request.GET.get('artist_search', '')
        if not artist_search and ('events' in referer or 'artist_pk' in referer):
            artist_search = self.request.session.get('artist_search_value', '')
        elif not self.request.GET.get('artist_pk'):
            if 'artist_search_value' in self.request.session:
                del self.request.session['artist_search_value']

        return artist_search

    def get_artist_context(self, q, artist_search):

        artist_id = self.request.GET.get('artist_pk')
        artist = None
        artists_blocks = None
        showing_artist_results = ''
        num_pages = 0

        search_input = None
        if not artist_id:
            artists_blocks, showing_artist_results, num_pages, search_input = self.search(
                Artist, q, artist_search=artist_search)
            if artists_blocks and len(artists_blocks[0]) == 1:
                artist=artists_blocks[0][0]

        artist = artist or Artist.objects.filter(id=artist_id).first()

        artist_context = {
            'artist_profile': bool(artist),
            'artist': artist,
            'artist_search': artist_search,
        }

        if not artist_id and artist:
            artist_id = artist.pk

        # Populate upcoming shows as well. That is the only case for now.
        upcoming_event_blocks, showing_event_results, upcoming_num_pages, first, last, search_input = self.search(
            Event, '', results_per_page=60,
            artist_pk=artist_id, date_from=datetime.datetime.today(), search_input=search_input)

        artist_context['upcoming_events'] = upcoming_event_blocks[0] if upcoming_event_blocks else []
        artist_context['showing_artist_results'] = showing_artist_results
        artist_context['artists_blocks'] = artists_blocks
        artist_context['artist_num_pages'] = num_pages

        return artist_context, search_input

    def get_instrument_context(self):

        context = {}
        instruments = Instrument.objects.all()
        artist_count = sum([i.artist_count for i in instruments])
        context['instruments_artist_count'] = artist_count
        context['instruments'] = instruments

        return context

    def get_context_data(self, **kwargs):

        referer = self.request.META.get('HTTP_REFERER', '')

        context = super(TemplateSearchView, self).get_context_data(**kwargs)
        context = self.get_upcoming_events_context_data(context)

        date_from, date_to = self.get_filter_dates(referer)
        artist_search = self.get_artist_search_filter(referer)
        query_term, query_context = self.get_query_context()
        context.update(query_context)

        artist_context, search_input = self.get_artist_context(query_term, artist_search)
        context.update(artist_context)

        instrument_context = self.get_instrument_context()
        context.update(instrument_context)

        artist_id = context['artist'].pk if context['artist'] else None
        event_blocks, showing_event_results, num_pages, first, last, search_input = self.search(
            Event, query_term, results_per_page=60, artist_pk=artist_id,
            date_from=date_from, date_to=date_to, search_input=search_input)

        context['showing_event_results'] = showing_event_results
        context['event_results'] = event_blocks[0] if event_blocks else []
        context['current_page'] = page = 1
        context['last_page'] = num_pages
        context['range'] = range(
            1, num_pages + 1)[:page][-3:] + range(1, num_pages + 1)[page:][:2]
        context['has_last_page'] = (num_pages - page) >= 3

        if event_blocks and event_blocks[0] and event_blocks[0][0].date:
            context['first_event_date'] = last.get_date().strftime('%m/%d/%Y')
            context['last_event_date'] = first.get_date().strftime('%m/%d/%Y')
            context['first'] = first
            context['last'] = last

        if self.request.user.is_staff:
            context['show_metrics'] = True

        context['user'] = self.request.user

        context['alphabet'] = string.ascii_lowercase
        context['query_term'] = query_term

        # check searched instruments
        instruments = search_input[1]
        if instruments:
            context['instrument'] = instruments[0]

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


class UpcomingSearchView(SearchMixin):

    template_name = 'search/upcoming_calendar_dates.html'

    def get_context_data(self, **kwargs):
        context = super(UpcomingSearchView, self).get_context_data(**kwargs)
        context.update(self.get_upcoming_context)
        return context

    def get_upcoming_context(self):
        context = {'day_list': []}
        days = int(self.request.GET.get('days', 12))
        starting_date = self.request.GET.get('starting_date', datetime.datetime.today().strftime('%Y-%m-%d'))
        starting_date = datetime.datetime.strptime(starting_date, '%Y-%m-%d')
        venue = self.request.GET.get('venue', 'all')
        event_list = Event.objects.filter(start__gte=starting_date)
        if not self.request.user.is_superuser:
            event_list = event_list.exclude(state=Event.STATUS.Draft)
        if venue:
            if venue != 'all':
                event_list = event_list.filter(venue__pk=venue)
        event_list = event_list.order_by('start')
        first_event = event_list.first()
        last_event = event_list.last()
        for day in range(0, days):
            # list of events for one day
            day_itinerary = {}
            day_start = starting_date + timedelta(days=day, hours=5)
            day_end = day_start + timedelta(days=1)
            day_itinerary['day_start'] = day_start
            day_itinerary['day_events'] = event_list.filter(start__gte=day_start, start__lte=day_end).order_by('start')
            context['day_list'].append(day_itinerary)

        context['first_event'] = first_event
        context['last_event'] = last_event
        context['new_date'] = (day_start + timedelta(days=1)).strftime('%Y-%m-%d')

        # Tonight events
        context['events_today'] = Event.objects.get_today_and_tomorrow_events(
            is_staff=self.request.user.is_staff
        )

        return context


class UpcomingSearchViewAjax2(TemplateView, UpcomingSearchView):

    template_name = 'search/upcoming_calendar_dates.html'

    def get_context_data(self, **kwargs):
        context = super(UpcomingSearchViewAjax, self).get_context_data(**kwargs)
        context.update(self.get_upcoming_context())

        return context


class UpcomingSearchViewAjax(TemplateView, UpcomingSearchView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update(self.get_upcoming_context())
        data = {
            'template': render_to_string(
                'search/upcoming_calendar_dates.html', context,
                context_instance=RequestContext(request)
            ),
            'new_date':  context['new_date'],
        }
        if 'first_event' in context and context['first_event']:
            data['first_date'] = context['first_event'].date.strftime('%Y-%m-%d')
        
        return JsonResponse(data)
