# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0026_auto_20190506_1041'),
        ('subscriptions', '0003_donation_deductable_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='product',
            field=models.ForeignKey(related_name='donations', blank=True, to='catalogue.Product', null=True),
            preserve_default=True,
        ),
    ]
