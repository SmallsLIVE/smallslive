# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def sum_artists(apps, schema_editor):
    # noinspection PyPep8Naming
    Instrument = apps.get_model('artists', 'Instrument')
    for instrument in Instrument.objects.all():
        instrument.artist_count = instrument.artists.count()
        instrument.save()


def dummy(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0021_artist_public_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='instrument',
            name='artist_count',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.RunPython(sum_artists, dummy)
    ]
