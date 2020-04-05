# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20180924_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallsuser',
            name='archive_access_until',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
