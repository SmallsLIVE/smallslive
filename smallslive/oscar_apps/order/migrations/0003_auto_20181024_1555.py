# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20141007_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(max_length=150, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(max_length=150, blank=True),
            preserve_default=True,
        ),
    ]
