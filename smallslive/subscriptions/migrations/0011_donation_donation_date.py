# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0010_donation_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='donation_date',
            field=models.DateField(default=datetime.date(2021, 1, 21)),
            preserve_default=True,
        ),
    ]
