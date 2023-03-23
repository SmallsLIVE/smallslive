# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20150326_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='state',
            field=model_utils.fields.StatusField(default=b'Published', max_length=100, no_check_for_status=True, choices=[(0, 'dummy')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recording',
            name='event',
            field=models.ForeignKey(related_name='recordings_info', on_delete=models.SET_NULL, to='events.Event'),
            preserve_default=True,
        ),
    ]
