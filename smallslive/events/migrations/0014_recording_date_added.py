# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_event_cropping'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 24, 14, 52, 7, 719214, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
