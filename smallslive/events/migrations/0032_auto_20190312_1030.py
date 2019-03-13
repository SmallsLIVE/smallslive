# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0031_event_streamable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='photo',
            field=events.models.CustomImageField(storage=events.models.get_event_media_storage, max_length=150, upload_to=b'event_images', blank=True),
            preserve_default=True,
        ),
    ]
