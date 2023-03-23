# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0010_artist_cropping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('photo', '580x400', hide_image_field=False, size_warning=False, allow_fullsize=True, free_crop=False, adapt_rotation=False, help_text=b'Enable cropping', verbose_name='cropping'),
            preserve_default=True,
        ),
    ]
