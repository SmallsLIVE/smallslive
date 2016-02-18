# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0017_auto_20160218_1228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='ledger_balance',
        ),
        migrations.AddField(
            model_name='artistearnings',
            name='ledger_balance',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=4),
            preserve_default=True,
        ),
    ]
