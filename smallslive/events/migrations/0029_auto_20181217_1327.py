# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0028_showdefaulttime'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='play_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='seconds_played',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
