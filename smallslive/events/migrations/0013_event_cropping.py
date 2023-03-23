# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_auto_20150331_0915'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('photo', '600x360', hide_image_field=False, size_warning=False, allow_fullsize=True, free_crop=False, adapt_rotation=False, help_text=b'Enable cropping', verbose_name='cropping'),
            preserve_default=True,
        ),
    ]
