# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0037_venue_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='stripe_secret_key',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        ),
    ]
