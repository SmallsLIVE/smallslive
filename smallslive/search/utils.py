def facets_by_model_name(sqs):
    facet_counts = sqs.facet_counts()
    fields = facet_counts.get('fields', {})
    facet_counts = {model: count for (model, count) in fields.get('model', [])}
    counts = {
        'artist_count': facet_counts.get('artist', 0),
        'event_count': facet_counts.get('event', 0),
        'instrument_count': facet_counts.get('instrument', 0),
    }
    return counts
