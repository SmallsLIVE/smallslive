# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0003_stockrecord_digital_download'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockrecord',
            name='is_hd',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
