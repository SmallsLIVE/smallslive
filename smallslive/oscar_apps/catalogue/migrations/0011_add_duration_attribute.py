# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_duration_attribute(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    ProductClass = apps.get_model("catalogue", "ProductClass")
    ProductAttribute = apps.get_model("catalogue", "ProductAttribute")
    track = ProductClass.objects.get(slug='track')

    ProductAttribute.objects.create(product_class=track, name="Duration", code="duration", type="text")


class Migration(migrations.Migration):
    dependencies = [
        ('catalogue', '0010_add_composer_attribute'),
    ]

    operations = [
        migrations.RunPython(add_duration_attribute),
    ]
