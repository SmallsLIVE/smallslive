# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0026_auto_20181001_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='start_streaming_before_minutes',
            field=models.IntegerField(default=15),
            preserve_default=True,
        ),
    ]
