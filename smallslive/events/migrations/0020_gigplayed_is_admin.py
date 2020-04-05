# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import F


def fill_is_admin(apps, schema_editor):
    # noinspection PyPep8Naming
    GigPlayed = apps.get_model('events', 'GigPlayed')
    GigPlayed.objects.all().update(is_admin=F('is_leader'))


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_event_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='gigplayed',
            name='is_admin',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RunPython(fill_is_admin, reverse_code=noop)
    ]
