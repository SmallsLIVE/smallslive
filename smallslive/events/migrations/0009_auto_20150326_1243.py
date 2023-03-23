# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0001_initial'),
        ('events', '0008_auto_20150326_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recording',
            name='media_file',
            field=models.ForeignKey(related_name='recording',on_delete=models.SET_NULL, to='multimedia.MediaFile', primary_key=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='recordings',
            field=models.ManyToManyField(to='multimedia.MediaFile', through='events.Recording'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recording',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, default=None, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recording',
            name='event',
            field=models.ForeignKey(to='events.Event', on_delete=models.SET_NULL),
            preserve_default=True,
        ),

    ]
