# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0020_usercatalogue_usercatalogueproduct'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usercatalogue',
            options={'verbose_name': 'Full access user'},
        ),
        migrations.AlterModelOptions(
            name='usercatalogueproduct',
            options={'verbose_name': 'Product access user'},
        ),
        migrations.AlterField(
            model_name='usercatalogue',
            name='user',
            field=models.ForeignKey(related_name='catalogue_access', to=settings.AUTH_USER_MODEL, unique=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='usercatalogueproduct',
            unique_together=set([('user', 'product')]),
        ),
    ]
