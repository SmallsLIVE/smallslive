# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0017_auto_20181218_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='event_set',
            field=models.ForeignKey(related_name='tickets', to='events.EventSet', null=True),
            preserve_default=True,
        ),
    ]
