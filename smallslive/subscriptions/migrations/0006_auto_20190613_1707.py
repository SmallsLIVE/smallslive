# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0033_auto_20190611_1704'),
        ('subscriptions', '0005_donation_artist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='artist',
        ),
        migrations.AddField(
            model_name='donation',
            name='event',
            field=models.ForeignKey(related_name='donations', blank=True, to='events.Event', null=True),
            preserve_default=True,
        ),
    ]
