# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multimedia.models
import multimedia.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0006_auto_20150623_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediafile',
            name='file',
            field=multimedia.fields.DynamicBucketFileField(upload_to=multimedia.models.media_file_path, blank=True),
            preserve_default=True,
        ),
    ]
