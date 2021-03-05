# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0041_event_minimum_sponsorship_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='sponsorship_enabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
