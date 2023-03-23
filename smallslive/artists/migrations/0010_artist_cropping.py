# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0009_auto_20150407_0627'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('photo', '580x400', hide_image_field=False, size_warning=False, allow_fullsize=False, free_crop=False, adapt_rotation=False, help_text=None, verbose_name='cropping'),
            preserve_default=True,
        ),
    ]
