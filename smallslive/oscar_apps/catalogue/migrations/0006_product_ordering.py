# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_setup_product_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ordering',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
