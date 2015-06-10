# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productattributevalue',
            name='value_file',
            field=models.FileField(max_length=255, null=True, upload_to=b'product_images/%Y/%m/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productattributevalue',
            name='value_image',
            field=models.ImageField(max_length=255, null=True, upload_to=b'product_images/%Y/%m/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productimage',
            name='original',
            field=models.ImageField(upload_to=b'product_images/%Y/%m/', max_length=255, verbose_name='Original'),
            preserve_default=True,
        ),
    ]
