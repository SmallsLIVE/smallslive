# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_event_recordings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recording',
            name='event',
            field=models.ForeignKey(related_name='recordings',  on_delete=models.SET_NULL, to='events.Event'),
            preserve_default=True,
        ),
    ]
