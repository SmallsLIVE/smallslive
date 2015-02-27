# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_extend_allauth_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallsuser',
            name='newsletter',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
