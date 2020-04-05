# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0036_auto_20190801_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
