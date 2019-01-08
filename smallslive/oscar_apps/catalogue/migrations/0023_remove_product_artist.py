# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0022_auto_20190108_0812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='artist',
        ),
    ]
