# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_auto_20191114_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='archive_access_expiry_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='donation',
            name='user',
            field=models.ForeignKey(related_name='donations',  on_delete=models.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
