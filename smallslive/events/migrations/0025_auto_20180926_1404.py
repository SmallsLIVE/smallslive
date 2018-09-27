# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_original_id_custom_image_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='audio_bucket_name',
            field=models.CharField(default=b'smallslivemp3', max_length=4096),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='venue',
            name='video_bucket_name',
            field=models.CharField(default=b'smallslivevid', max_length=4096),
            preserve_default=True,
        ),
    ]
