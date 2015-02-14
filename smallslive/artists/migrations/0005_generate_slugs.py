# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    Artist = apps.get_model("artists", "Artist")
    for artist in Artist.objects.all():
        artist.slug = slugify("{0} {1}".format(artist.first_name, artist.last_name))
        artist.save()


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0004_artist_slug'),
    ]

    operations = [
        migrations.RunPython(generate_slugs),
    ]
