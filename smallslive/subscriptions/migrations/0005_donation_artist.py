# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0021_artist_public_email'),
        ('subscriptions', '0004_donation_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='artist',
            field=models.ForeignKey(related_name='donations', blank=True, to='artists.Artist', null=True),
            preserve_default=True,
        ),
    ]
