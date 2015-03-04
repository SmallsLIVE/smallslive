import datetime
from haystack import indexes
from elasticstack import fields
from .models import Artist, Instrument


class ArtistIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    instruments = indexes.MultiValueField(null=True)
    model = indexes.CharField(model_attr="_meta__verbose_name", faceted=True)

    def get_model(self):
        return Artist

    def prepare_instruments(self, obj):
        return [instrument.id for instrument in obj.instruments.all()] or None


class InstrumentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, model_attr='name')
    model = indexes.CharField(model_attr='_meta__verbose_name', faceted=True)

    def get_model(self):
        return Instrument
