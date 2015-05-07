# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_smallsuser_artist'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallsuser',
            name='taxpayer_id',
            field=models.CharField(max_length=15, blank=True),
            preserve_default=True,
        ),
    ]
