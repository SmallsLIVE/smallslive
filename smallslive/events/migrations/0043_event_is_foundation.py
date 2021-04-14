# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0042_event_sponsorship_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_foundation',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
