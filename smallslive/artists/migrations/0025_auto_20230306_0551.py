# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import storages.backends.s3boto


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0024_auto_20200511_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastpayoutperiod',
            name='admin_payout_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pastpayoutperiod',
            name='donations_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pastpayoutperiod',
            name='musicians_payout_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='payoutperiodgeneration',
            name='admin_payout_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts_generation/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='payoutperiodgeneration',
            name='donations_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts_generation/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='payoutperiodgeneration',
            name='musicians_payout_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts_generation/', blank=True),
            preserve_default=True,
        ),
    ]
