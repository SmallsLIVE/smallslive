# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0040_auto_20200205_1449'),
        ('subscriptions', '0012_donation_populate_donation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='sponsored_event',
            field=models.OneToOneField(related_name='sponsorship',  on_delete=models.SET_NULL, null=True, blank=True, to='events.Event'),
            preserve_default=True,
        ),
    ]
