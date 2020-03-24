# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import storages.backends.s3boto


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0022_instrument_artist_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayoutPeriodGeneration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('total_seconds', models.BigIntegerField(default=0)),
                ('total_amount', models.DecimalField(default=0, max_digits=10, decimal_places=4)),
                ('admin_payout_spreadsheet', models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True)),
                ('musicians_payout_spreadsheet', models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True)),
                ('donations_spreadsheet', models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True)),
                ('calculation_start', models.DateTimeField(auto_now_add=True)),
                ('calculation_end', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(blank=True, max_length=255, choices=[(b'initial', b'initial'), (b'processing', b'processing'), (b'success', b'success'), (b'error', b'error')])),
                ('status_message', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='pastpayoutperiod',
            old_name='payout_spreadsheet',
            new_name='admin_payout_spreadsheet',
        ),
        migrations.AddField(
            model_name='pastpayoutperiod',
            name='donations_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pastpayoutperiod',
            name='musicians_payout_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
    ]
