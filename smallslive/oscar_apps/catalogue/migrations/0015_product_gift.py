# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_auto_20181018_2252'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='gift',
            field=models.BooleanField(default=False, help_text=b'Make this product a gift in the store'),
            preserve_default=True,
        ),
    ]
