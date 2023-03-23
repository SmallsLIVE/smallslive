# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20150326_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='title',
            field=models.CharField(max_length=150, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='recording',
            name='media_file',
            field=models.ForeignKey(related_name='set', on_delete=models.SET_NULL, primary_key=True, serialize=False, to='multimedia.MediaFile'),
            preserve_default=True,
        ),
    ]
