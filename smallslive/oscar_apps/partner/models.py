from django.db import models

from oscar.apps.partner.abstract_models import AbstractStockRecord


class StockRecord(AbstractStockRecord):
    digital_download = models.OneToOneField('multimedia.MediaFile', blank=True, null=True, related_name='stock_record')

from oscar.apps.partner.models import *  # noqa
