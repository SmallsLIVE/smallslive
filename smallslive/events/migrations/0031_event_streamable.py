# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0030_auto_20181227_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='streamable',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
