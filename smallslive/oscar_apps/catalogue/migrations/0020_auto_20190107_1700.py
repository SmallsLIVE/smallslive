# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0019_product_artist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='artist',
        ),
        migrations.AddField(
            model_name='product',
            name='artist',
            field=models.ManyToManyField(to='artists.Artist', null=True, verbose_name=b'Attributes', blank=True),
            preserve_default=True,
        ),
    ]
