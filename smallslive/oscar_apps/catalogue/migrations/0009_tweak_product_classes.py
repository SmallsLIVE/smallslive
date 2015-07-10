# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def tweak_product_classes(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Product = apps.get_model("catalogue", "Product")
    ProductClass = apps.get_model("catalogue", "ProductClass")
    ProductClass.objects.filter(slug='physical_album').update(slug='physical-album')
    digital_album = ProductClass.objects.create(name='Digital album',
                                                slug='digital-album',
                                                requires_shipping=False,
                                                track_stock=False)


class Migration(migrations.Migration):
    dependencies = [
        ('catalogue', '0008_product_featured'),
    ]

    operations = [
        migrations.RunPython(tweak_product_classes),
    ]
