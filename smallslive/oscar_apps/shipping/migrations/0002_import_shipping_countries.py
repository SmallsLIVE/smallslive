# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import management
from django.db import models, migrations


def load_shipping_countries(apps, schema_editor):
    management.call_command('oscar_populate_countries')


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_shipping_countries),
    ]
