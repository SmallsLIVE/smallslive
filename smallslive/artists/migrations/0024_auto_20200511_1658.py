# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0023_auto_20200317_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastpayoutperiod',
            name='admin_payout_spreadsheet',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pastpayoutperiod',
            name='donations_spreadsheet',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pastpayoutperiod',
            name='musicians_payout_spreadsheet',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='payoutperiodgeneration',
            name='admin_payout_spreadsheet',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'payouts_generation/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='payoutperiodgeneration',
            name='donations_spreadsheet',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'payouts_generation/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='payoutperiodgeneration',
            name='musicians_payout_spreadsheet',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=b'payouts_generation/', blank=True),
            preserve_default=True,
        ),
    ]
