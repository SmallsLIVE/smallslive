# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multimedia.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0003_auto_20150330_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='sd_video_file',
            field=multimedia.fields.DynamicBucketFileField(upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
