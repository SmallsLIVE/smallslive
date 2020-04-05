# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0039_venue_foundation'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='paypal_client_id',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='venue',
            name='paypal_client_secret',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        ),
    ]
