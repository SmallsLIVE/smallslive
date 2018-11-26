# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0015_product_gift'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='gift_price',
            field=models.DecimalField(help_text=b'Set the gift price', null=True, max_digits=12, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
