# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0016_auto_20160218_0903'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='artistearnings',
            options={'ordering': ['-payout_period__period_end']},
        ),
        migrations.AlterModelOptions(
            name='pastpayoutperiod',
            options={'ordering': ['-period_end']},
        ),
        migrations.AddField(
            model_name='artist',
            name='ledger_balance',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=4),
            preserve_default=True,
        ),
    ]
