# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import management
from django.db import models, migrations


def load_instruments(apps, schema_editor):
    management.call_command('loaddata', 'instruments.json')


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0002_artist_user'),
    ]

    operations = [
       migrations.RunPython(load_instruments),
    ]
