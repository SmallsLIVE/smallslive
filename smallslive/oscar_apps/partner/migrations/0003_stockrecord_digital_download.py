# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0004_mediafile_sd_video_file'),
        ('partner', '0002_auto_20141007_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockrecord',
            name='digital_download',
            field=models.OneToOneField(related_name='stock_record', on_delete=models.SET_NULL, null=True, blank=True, to='multimedia.MediaFile'),
            preserve_default=True,
        ),
    ]
