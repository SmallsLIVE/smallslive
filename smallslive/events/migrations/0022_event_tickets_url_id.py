# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_venue_tickets_url_format'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='tickets_url_id',
            field=models.CharField(
                help_text=b'Identifier for the ticket provider, eg: 4124-polite-jam-session-with-naama-gheber',
                max_length=100,
                null=True,
                blank=True),
            preserve_default=True,
        ),
    ]
