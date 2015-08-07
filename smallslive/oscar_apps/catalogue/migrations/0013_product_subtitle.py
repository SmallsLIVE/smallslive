# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20150804_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='subtitle',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
