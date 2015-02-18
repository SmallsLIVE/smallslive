import datetime
from haystack import indexes
from .models import Event


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', boost=1.5)
    start = indexes.DateTimeField(model_attr='start')  # needed for results sorting

    def get_model(self):
        return Event
