import json
from itertools import chain
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from haystack.query import SearchQuerySet
from .utils import facets_by_model_name
from events.models import Event
from artists.models import Artist
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.template import RequestContext


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

class GlobalSearchView(TemplateView):
    template_name = 'search/search.html'

    def get_context_data(self, **kwargs):
        context = super(GlobalSearchView, self).get_context_data(**kwargs)
        
        q = self.request.GET.get('q', '')
        artist_sqs = SearchQuerySet().models(Artist).filter(content=q)
        artists_blocks = []
        artist_block = []

        paginator = Paginator(artist_sqs, 48)

        for item in paginator.page(1):
            item = Artist.objects.filter(pk=item.pk).first()
            artist_block.append(item)

            if len(artist_block) == 8:
                artists_blocks.append(artist_block)
                artist_block = []

        if artist_block:
            artists_blocks.append(artist_block)
            artist_block = []
        
        #context['artist_subheader'] = artist_subheader
        context['artists_blocks'] = artists_blocks
        
        
        
        
        #print(Artist.objects.filter(pk=item.pk).first().__dict__)

        event_sqs = SearchQuerySet().models(Event).filter(content=q).order_by('title')
        events = []
        paginator = Paginator(event_sqs, 15)
        for item in paginator.page(1):
            item = Event.objects.filter(pk=item.pk).first()
            events.append(item)

        context['event_results'] = events

        #context['event_results'] = Event.objects.exclude(
        #        state=Event.STATUS.Draft
        #   ).order_by('-start')[:15]

        return context

# heredar de view y hacer un mixin
def get_artists(request):
    q = request.GET.get('q', None)
    artist_page = int(request.GET.get('artist-page', 1))

    artist_sqs = SearchQuerySet().models(Artist).filter(content=q)
    artists_blocks = []
    artist_block = []

    paginator = Paginator(artist_sqs, 48)

    paginator.page(1).object_list  # if this line is removed the paginator.page() returns the same items. Bug?

    for item in paginator.page(artist_page).object_list:
        item = Artist.objects.filter(pk=item.pk).first()
        artist_block.append(item)

        if len(artist_block) == 8:
            artists_blocks.append(artist_block)
            artist_block = []

    if artist_block:
        artists_blocks.append(artist_block)
        artist_block = []
    
    context={'artists_blocks': artists_blocks}
    template = 'search/artist_results.html'
    temp = render_to_string(template,
        context,
        context_instance=RequestContext(request)
    )

    data = {
        'artists': temp
    }
    
    return JsonResponse(data)
    
