# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institutional_subscriptions', '0002_remove_institution_subscription_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='subscription_end',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
