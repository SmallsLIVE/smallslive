# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def setup_product_models(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Product = apps.get_model("catalogue", "Product")
    ProductClass = apps.get_model("catalogue", "ProductClass")
    ProductAttribute = apps.get_model("catalogue", "ProductAttribute")
    Product.objects.all().delete()
    ProductClass.objects.all().delete()
    album = ProductClass.objects.create(name='Album',
                                        slug='album',
                                        requires_shipping=False,
                                        track_stock=False)
    track = ProductClass.objects.create(name='Track',
                                        slug='track',
                                        requires_shipping=False,
                                        track_stock=False)
    physical_album = ProductClass.objects.create(name='Physical album',
                                                 slug='physical_album',
                                                 requires_shipping=True,
                                                 track_stock=True)

    ProductAttribute.objects.create(product_class=track, name="Track number", code="track_no", type="integer")
    ProductAttribute.objects.create(product_class=track, name="Author", code="author", type="text")


class Migration(migrations.Migration):
    dependencies = [
        ('catalogue', '0004_auto_20150617_1804'),
    ]

    operations = [
        migrations.RunPython(setup_product_models),
    ]
