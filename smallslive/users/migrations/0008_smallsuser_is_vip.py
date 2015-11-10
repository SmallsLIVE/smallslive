# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_smallsuser_taxpayer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallsuser',
            name='is_vip',
            field=models.BooleanField(default=False, help_text=b'Designates whether this user is a VIP and has access to audio and video without paying for a subscription'),
            preserve_default=True,
        ),
    ]
