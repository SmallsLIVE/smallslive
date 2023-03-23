# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields
import storages.backends.s3boto


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0019_pastpayoutperiod_payout_spreadsheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name=b'cropping',
            field=image_cropping.fields.ImageRatioField('photo', '580x580', hide_image_field=False, size_warning=False, allow_fullsize=True, free_crop=False, adapt_rotation=False, help_text=b'Enable cropping', verbose_name='cropping'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pastpayoutperiod',
            name='payout_spreadsheet',
            field=models.FileField(storage=storages.backends.s3boto.S3BotoStorage(), upload_to=b'payouts/', blank=True),
            preserve_default=True,
        ),
    ]
