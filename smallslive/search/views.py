import json
from itertools import chain
from django.http import HttpResponse
from haystack.query import SearchQuerySet
from .utils import facets_by_model_name


def search_autocomplete(request):
    sqs = SearchQuerySet().autocomplete(content=request.GET.get('term', '')).facet('model')
    artists = sqs.filter(model_exact="artist")[:5]
    events = sqs.filter(model_exact="event")[:5]
    instruments = sqs.filter(model_exact="instrument")[:5]
    suggestions = [{'label': result.object.autocomplete_label(),
                    'sublabel': result.object.autocomplete_sublabel(),
                    'category': result.model_exact,
                    'url': result.object.get_absolute_url()} for result in chain(artists, events, instruments)]

    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    the_data = json.dumps({
        'results': suggestions,
        'counts': facets_by_model_name(sqs)
    })
    resp = HttpResponse(the_data, content_type='application/json')
    return resp
