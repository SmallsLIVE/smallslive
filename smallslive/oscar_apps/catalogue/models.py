from django.db import models
from django.utils.functional import cached_property

from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    short_description = models.TextField(blank=True)
    event = models.ForeignKey('events.Event', blank=True, null=True, related_name='products')
    album = models.ForeignKey('self', blank=True, null=True, related_name='tracks')  # used for album/track
    ordering = models.PositiveIntegerField(default=0)  # explicit ordering, usually for tracks on an album
    preview = models.OneToOneField('multimedia.MediaFile', blank=True, null=True, related_name='product')

    def get_track_preview_url(self):
        if self.preview_id:
            return self.preview.get_file_url()

    @cached_property
    def get_track_stockrecord(self):
        if self.product_class.slug == "track":
            return self.stockrecords.filter(is_hd=False).first()

    @cached_property
    def get_hd_track_stockrecord(self):
        if self.product_class.slug == "track":
            return self.stockrecords.filter(is_hd=True).first()

from oscar.apps.catalogue.models import *
