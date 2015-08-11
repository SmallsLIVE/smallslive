# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multimedia.models
import multimedia.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0007_20150629_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediafile',
            name='file',
            field=multimedia.fields.DynamicBucketFileField(upload_to=multimedia.models.media_file_path, blank=True, max_length=300),
            preserve_default=True,
        ),
    ]
