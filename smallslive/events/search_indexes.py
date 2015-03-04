import datetime
from haystack import indexes
from .models import Event


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', boost=1.5)
    start = indexes.DateTimeField(model_attr='start')  # needed for results sorting
    model = indexes.CharField(model_attr='_meta__verbose_name', faceted=True)
    performers = indexes.MultiValueField(null=True)
    content_auto = indexes.EdgeNgramField(model_attr='title')

    def get_model(self):
        return Event

    def prepare_performers(self, obj):
        return [artist.id for artist in obj.performers.all()] or None
