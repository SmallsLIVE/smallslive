# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multimedia.models
import multimedia.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0004_mediafile_sd_video_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='category',
            field=models.CharField(blank=True, max_length=10, editable=False, choices=[(b'set', b'set'), (b'track', b'track'), (b'preview', b'preview')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mediafile',
            name='file',
            field=multimedia.fields.DynamicBucketFileField(upload_to=multimedia.models.media_file_path),
            preserve_default=True,
        ),
    ]
