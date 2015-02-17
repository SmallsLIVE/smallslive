# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    for event in Event.objects.all():
        event.slug = slugify(event.title)
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_event_slug'),
    ]

    operations = [
        migrations.RunPython(generate_slugs),
    ]
