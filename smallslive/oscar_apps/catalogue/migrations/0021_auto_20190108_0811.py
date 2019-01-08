# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0020_auto_20190107_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='event_set',
            field=models.ForeignKey(related_name='artist_list', to='events.EventSet', null=True),
            preserve_default=True,
        ),
    ]
