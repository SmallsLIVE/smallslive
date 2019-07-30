# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0034_auto_20190709_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='aws_access_key_id',
            field=models.CharField(max_length=4096, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='venue',
            name='aws_secret_access_key',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='venue',
            name='aws_storage_bucket_name',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='venue',
            name='stripe_publishable_key',
            field=models.CharField(max_length=4096, null=True, blank=True),
            preserve_default=True,
        ),
    ]
