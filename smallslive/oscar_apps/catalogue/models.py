from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProduct


class Product(AbstractProduct):
    short_description = models.TextField(blank=True)

from oscar.apps.catalogue.models import *
