# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multimedia.s3_storages
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0023_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='import_date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='original_id',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='photo',
            field=events.models.CustomImageField(storage=multimedia.s3_storages.ImageS3Storage(), max_length=150, upload_to=b'event_images', blank=True),
            preserve_default=True,
        ),
    ]
