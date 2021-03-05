# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0040_auto_20200205_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='minimum_sponsorship_amount',
            field=models.IntegerField(default=600),
            preserve_default=True,
        ),
    ]
