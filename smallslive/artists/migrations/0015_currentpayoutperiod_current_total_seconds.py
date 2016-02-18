# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0014_currentpayoutperiod'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentpayoutperiod',
            name='current_total_seconds',
            field=models.BigIntegerField(default=0),
            preserve_default=True,
        ),
    ]
