# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0014_auto_20210226_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='donation_date',
            field=models.DateField(default=datetime.date(2023, 3, 6)),
            preserve_default=True,
        ),
    ]
