# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_donation_confirmed'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='deductable_amount',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=12, decimal_places=2),
            preserve_default=True,
        ),
    ]
