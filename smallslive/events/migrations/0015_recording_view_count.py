# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_recording_date_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='view_count',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
