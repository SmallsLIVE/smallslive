# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0026_auto_20190506_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistproduct',
            name='is_leader',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
