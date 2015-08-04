# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_add_duration_attribute'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['ordering', 'title'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterField(
            model_name='product',
            name='featured',
            field=models.BooleanField(default=False, help_text=b'Make this product featured in the store'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='ordering',
            field=models.PositiveIntegerField(default=1000, help_text=b'Product ordering number, lower numbers come first when ordering'),
            preserve_default=True,
        ),
    ]
