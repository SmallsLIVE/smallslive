# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0005_generate_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='instruments',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, related_name='artists', to='artists.Instrument', blank=True),
            preserve_default=True,
        ),
    ]
