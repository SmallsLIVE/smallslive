# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0027_artistproduct_is_leader'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artistproduct',
            options={'ordering': ['sort_order'], 'verbose_name': 'Artist', 'verbose_name_plural': 'Artist list'},
        ),
        migrations.AddField(
            model_name='artistproduct',
            name='sort_order',
            field=models.CharField(max_length=30, blank=True),
            preserve_default=True,
        ),
    ]
