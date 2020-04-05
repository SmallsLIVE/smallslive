# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_auto_20190322_1034'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='artist',
            new_name='artists',
        ),
    ]
