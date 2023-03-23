# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0006_auto_20150623_1128'),
        ('catalogue', '0006_product_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='preview',
            field=models.OneToOneField(related_name='product', on_delete=models.SET_NULL, null=True, blank=True, to='multimedia.MediaFile'),
            preserve_default=True,
        ),
    ]
