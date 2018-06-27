import json
from itertools import chain
from dateutil import parser

from artists.models import Artist, Instrument
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.db.models import Q
from events.models import Event, Recording
from haystack.query import SearchQuerySet, SQ

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

    def get_instrument(self, text_array):

        condition = Q(name__icontains=text_array[0])
        for text in text_array[1:]:
            condition |= Q(name__icontains=text)
        return Instrument.objects.filter(condition).distinct().first()
    
    def get_instruments(self):
        return [i.name.upper() for i in Instrument.objects.all()]

    def search(self, entity, main_search, page=1, order=None, instrument=None, date=None, artist_search=None):

        if entity == Artist:
            results_per_page = 48
            sqs = entity.objects.all()
            words = main_search.split(' ')
            all_instruments = self.get_instruments()
            instruments = [i for i in words if i.upper() in all_instruments]
            words = [i for i in words if i.upper() not in all_instruments]
            if instruments:
                condition = Q(instruments__name__iexact=instruments[0])
                for i in instruments[1:]:
                    condition |= Q(instruments__name__iexact=i)
                sqs = entity.objects.filter(condition).distinct()
            if instrument:
                sqs = sqs.filter(instruments__name=instrument)
            if words:
                artist = words.pop()
                condition = Q(
                    last_name__icontains=artist) | Q(
                    first_name__icontains=artist)
                for artist in words:
                    condition |= Q(
                        last_name__icontains=artist) | Q(
                        first_name__icontains=artist)
                sqs = sqs.filter(condition).distinct()
            
            if artist_search:
                artist_words = artist_search.split(' ')
                artist = artist_words[0]
                good_matches = sqs.filter(Q(
                    last_name__istartswith=artist)).distinct()
                not_so_good_matches = sqs.filter(~Q(
                    last_name__istartswith=artist) & Q(
                    first_name__istartswith=artist)).distinct()
                sqs = list(good_matches) + list(not_so_good_matches)
            
        elif entity == Event:
            results_per_page = 15

            order = {
                'newest': '-start',
                'oldest': 'start',
                'popular': 'popular',
            }.get(order, '-start')
            
            if not main_search:
                sqs = entity.objects.all()
            else:
                words = main_search.split(' ')
                all_instruments = self.get_instruments()

                instruments = [i for i in words if i.upper() in all_instruments]
                words = [i for i in words if i.upper() not in all_instruments]

                if instruments:
                    condition = Q(artists_gig_info__role__name__icontains=instruments[0],
                        artists_gig_info__is_leader=True)
                    for i in instruments[1:]:
                        condition |= Q(artists_gig_info__role__name__icontains=i,
                            artists_gig_info__is_leader=True)
                    sqs = entity.objects.filter(condition).distinct()
                
                if words:
                    artist = words.pop()
                    condition = Q(
                        title__icontains=artist) | Q(
                        description__icontains=artist) | Q(
                        performers__first_name__icontains=artist) | Q(
                        performers__last_name__icontains=artist)
                    for artist in words:
                        condition |= Q(
                            title__icontains=artist) | Q(
                            description__icontains=artist) | Q(
                            performers__first_name__icontains=artist) | Q(
                            performers__last_name__icontains=artist)
                    sqs = sqs.filter(condition).distinct()
                

#                instrument = self.get_instrument(main_search.split(' '))
#                if instrument:
#                    sqs = entity.objects.filter(
#                        artists_gig_info__role__name__icontains=instrument.name,
#                        artists_gig_info__is_leader=True)
#
#                    for i in [i for i in main_search.split(' ') if i.lower() not in [instrument.name.lower()]]:
#                        sqs = sqs.filter(Q(
#                            title__icontains=main_search) | Q(
#                            description__icontains=i) | Q(
#                            performers__first_name__icontains=i) | Q(
#                            performers__last_name__icontains=i)).distinct()
#                else:
#                    sqs = entity.objects.all()
#                    for main_search in main_search.split(' '):
#                        sqs = sqs.filter(Q(
#                            title__icontains=main_search) | Q(
#                            description__icontains=main_search) | Q(
#                            performers__first_name__icontains=main_search) | Q(
#                            performers__last_name__icontains=main_search)).distinct()

            sqs = sqs.filter(recordings__media_file__isnull=False, recordings__state=Recording.STATUS.Published)
            
            if date:
                sqs = sqs.filter(start__gte=date)
            
            if order == 'popular':
                sqs = sqs.most_popular()
            else:
                sqs = sqs.order_by(order)

        blocks = []
        block = []

        paginator = Paginator(sqs, results_per_page)

        for item in paginator.page(page).object_list:
            item = entity.objects.filter(pk=item.pk).first()
            block.append(item)

            if len(block) == 8 and entity == Artist:
                blocks.append(block)
                block = []

        if block:
            blocks.append(block)
            block = []

        if paginator.count:
            showing_results = 'SHOWING {} - {} OF {} RESULTS'.format(
                1 + ((page - 1) * results_per_page),
                results_per_page + ((page - 1) * results_per_page) if page != paginator.num_pages else len(
                    paginator.page(page).object_list) + ((page - 1) * results_per_page),
                paginator.count)
        else:
            showing_results = 'NO RESULTS'

        return blocks, showing_results, paginator.num_pages

class MainSearchView(View, SearchMixin):

    def get(self, request, *args, **kwargs):
        main_search = request.GET.get('main_search', None)
        artist_search = request.GET.get('artist_search', None)
        page = int(request.GET.get('page', 1))
        entity = self.kwargs.get('entity', None)
        order = request.GET.get('order', None)
        instrument = request.GET.get('instrument', None)
        date = request.GET.get('date', None)

        if date:
            date = parser.parse(date, fuzzy=True)
        
        if entity == 'artist':
            artists_blocks, showing_results, num_pages = self.search(Artist, main_search, page, instrument=instrument, artist_search=artist_search)

            context={'artists_blocks': artists_blocks}
            template = 'search/artist_results.html'
            
        elif entity == 'event':
            events, showing_results, num_pages = self.search(Event, main_search, page, order=order, date=date)

            context={'events': events[0] if events else []}
            template = 'search/event_results.html'
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
            context={'actual_page': page,
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


class TemplateSearchView(TemplateView, SearchMixin):
    template_name = 'search/search.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateSearchView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q', '')

        artists_blocks, showing_artist_results, num_pages = self.search(Artist, q)

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
        context['range'] = range(1, num_pages + 1)[:page][-3:] + range(1, num_pages + 1)[page:][:2]
        context['has_last_page'] = (num_pages - page) >= 3
        
        return context
