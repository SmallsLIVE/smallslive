# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20150514_1418'),
        ('catalogue', '0003_product_short_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='album',
            field=models.ForeignKey(related_name='tracks', on_delete=models.SET_NULL, blank=True, to='catalogue.Product', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='event',
            field=models.ForeignKey(related_name='products', on_delete=models.SET_NULL, blank=True, to='events.Event', null=True),
            preserve_default=True,
        ),
    ]
