# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_order_order_type'),
        ('subscriptions', '0009_donation_artist'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='order',
            field=models.ForeignKey(related_name='donations',  on_delete=models.SET_NULL, blank=True, to='order.Order', null=True),
            preserve_default=True,
        ),
    ]
