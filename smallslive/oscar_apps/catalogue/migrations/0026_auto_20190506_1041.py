# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0025_artistproduct_instrument'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='artistproduct',
            unique_together=set([('product', 'artist', 'instrument')]),
        ),
    ]
