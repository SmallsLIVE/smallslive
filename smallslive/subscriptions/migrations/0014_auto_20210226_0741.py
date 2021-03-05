# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0013_auto_20210225_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='sponsored_event_dedication',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
