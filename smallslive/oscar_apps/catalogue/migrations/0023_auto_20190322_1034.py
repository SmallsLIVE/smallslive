# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def migrate_lines(apps, schema_editor):
    Line = apps.get_model('order', 'Line')
    UserCatalogueProduct = apps.get_model('catalogue', 'UserCatalogueProduct')

    for line in Line.objects.all().select_related('order__user', 'product__product_class'):
        if not line.product:
            if line.product:
                if not line.product.product_class:
                    if not line.order.user:
                        if line.product.product_class.slug in ['physical-album', 'digital-album']:
                            UserCatalogueProduct.objects.get_or_create(user=line.order.user, product=line.product)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0022_auto_20190320_1000'),
        ('order', '0002_auto_20141007_2032'),
    ]

    operations = [
        migrations.RunPython(migrate_lines),
    ]
