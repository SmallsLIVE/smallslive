from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    short_description = models.TextField(blank=True)
    event = models.ForeignKey('events.Event', blank=True, null=True, related_name='products')
    album = models.ForeignKey('self', blank=True, null=True, related_name='tracks')  # used for album/track
    ordering = models.PositiveIntegerField(default=0)  # explicit ordering, usually for tracks on an album

from oscar.apps.catalogue.models import *
