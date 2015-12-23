# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institutional_subscriptions', '0003_auto_20151223_0606'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='contact_email',
            field=models.EmailField(max_length=150, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='contact_name',
            field=models.CharField(max_length=150, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='contact_phone',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='notes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='institution',
            name='user_quota',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
