# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0026_auto_20190108_1239'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artistproduct',
            options={'ordering': ['product', 'artist'], 'verbose_name': 'Artist', 'verbose_name_plural': 'Artist list'},
        ),
        migrations.AlterUniqueTogether(
            name='artistproduct',
            unique_together=set([('product', 'artist')]),
        ),
    ]
