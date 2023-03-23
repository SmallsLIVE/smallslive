# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0022_instrument_artist_count'),
        ('subscriptions', '0008_auto_20191217_0759'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='artist',
            field=models.ForeignKey(related_name='donations',  on_delete=models.SET_NULL, blank=True, to='artists.Artist', null=True),
            preserve_default=True,
        ),
    ]
