# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0018_auto_20160218_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='pastpayoutperiod',
            name='payout_spreadsheet',
            field=models.FileField(upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
