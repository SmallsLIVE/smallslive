# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_remove_product_artist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='artist_list',
            new_name='artist',
        ),
    ]
