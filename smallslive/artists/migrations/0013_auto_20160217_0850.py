# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0012_auto_20160104_1217'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artistearnings',
            options={'ordering': ['-period_start']},
        ),
        migrations.AddField(
            model_name='artist',
            name='current_period_ratio',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=10),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='current_period_seconds_played',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
    ]
