# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_product_subtitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='set',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='event',
            field=models.ForeignKey(related_name='products', on_delete=models.SET_NULL, to='events.Event', null=True),
            preserve_default=True,
        ),
    ]
