# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0038_venue_stripe_secret_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='foundation',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
