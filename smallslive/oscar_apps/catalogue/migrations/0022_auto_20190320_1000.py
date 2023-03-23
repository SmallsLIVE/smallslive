# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_access(apps, schema_editor):
    SmallsUser = apps.get_model('users', 'SmallsUser')
    UserCatalogue = apps.get_model('catalogue', 'UserCatalogue')

    UserCatalogue.objects.all().delete()
    for user in SmallsUser.objects.all():
        UserCatalogue.objects.get_or_create(user=user)


def migrate_lines(apps, schema_editor):
    Line = apps.get_model('order', 'Line')
    UserCatalogueProduct = apps.get_model('catalogue', 'UserCatalogueProduct')

    UserCatalogueProduct.objects.all().delete()
    for line in Line.objects.all().select_related('order__user', 'product__product_class'):
        if not line.product:
            print('Not product: ', line.id)
        elif not line.product.product_class:
            print('Not product class: ', line.product.id, line.product.title)
        elif not line.order.user:
            print('Not order user: ', line.order.id)
        elif line.product.product_class.name in ['Album', 'Track', 'CD']:
            UserCatalogueProduct.objects.get_or_create(user=line.order.user, product=line.product)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0021_auto_20190320_0910'),
        ('order', '0002_auto_20141007_2032'),
    ]

    operations = [
        migrations.RunPython(migrate_access),
        migrations.RunPython(migrate_lines),
    ]
