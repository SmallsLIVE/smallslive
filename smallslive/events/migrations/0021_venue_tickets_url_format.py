# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_gigplayed_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='tickets_url_format',
            field=models.CharField(
                max_length=255,
                help_text=b'eg: https://www.mezzrow.com/events/{event_id}',
                null=True,
                blank=True),
            preserve_default=True,
        ),
    ]
