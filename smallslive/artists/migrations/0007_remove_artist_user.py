# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0006_add_instruments_related_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='user',
        ),
    ]
