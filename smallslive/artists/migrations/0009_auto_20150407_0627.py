# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0008_auto_20150401_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='website',
            field=models.URLField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
