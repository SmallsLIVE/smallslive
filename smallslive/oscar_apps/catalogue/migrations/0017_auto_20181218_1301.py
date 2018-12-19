# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0029_auto_20181217_1327'),
        ('catalogue', '0016_product_gift_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='event_set',
            field=models.ForeignKey(related_name='products', to='events.EventSet', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='event',
            field=models.ForeignKey(related_name='products', blank=True, to='events.Event', null=True),
            preserve_default=True,
        ),
    ]
