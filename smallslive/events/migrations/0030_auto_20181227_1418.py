# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0029_auto_20181217_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showdefaulttime',
            name='second_set',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
