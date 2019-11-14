# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0006_auto_20190613_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='user',
            field=models.ForeignKey(related_name='donations', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
