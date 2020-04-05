# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0035_auto_20190730_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showdefaulttime',
            name='venue',
            field=models.ForeignKey(related_name='default_times', to='events.Venue'),
            preserve_default=True,
        ),
    ]
