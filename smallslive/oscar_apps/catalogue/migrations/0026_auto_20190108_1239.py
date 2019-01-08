# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0025_auto_20190108_0926'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artistproduct',
            options={'verbose_name': 'Artist list'},
        ),
    ]
