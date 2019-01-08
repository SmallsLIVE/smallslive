# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0021_artist_public_email'),
        ('catalogue', '0018_auto_20181219_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='artist',
            field=models.ForeignKey(related_name='artist', blank=True, to='artists.Artist', null=True),
            preserve_default=True,
        ),
    ]
