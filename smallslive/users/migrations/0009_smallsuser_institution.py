# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institutional_subscriptions', '0001_initial'),
        ('users', '0008_smallsuser_is_vip'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallsuser',
            name='institution',
            field=models.ForeignKey(related_name='members',  on_delete=models.SET_NULL, blank=True, to='institutional_subscriptions.Institution', null=True),
            preserve_default=True,
        ),
    ]
