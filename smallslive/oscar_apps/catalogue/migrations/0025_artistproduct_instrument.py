# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0021_artist_public_email'),
        ('catalogue', '0024_auto_20190506_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistproduct',
            name='instrument',
            field=models.ForeignKey(blank=True, to='artists.Instrument', null=True),
            preserve_default=True,
        ),
    ]
