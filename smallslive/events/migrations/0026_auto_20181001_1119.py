# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0025_auto_20180926_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='tickets_url_id',
        ),
        migrations.RemoveField(
            model_name='venue',
            name='tickets_url_format',
        ),
        migrations.AddField(
            model_name='event',
            name='tickets_url',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
