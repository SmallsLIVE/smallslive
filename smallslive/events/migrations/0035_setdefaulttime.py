# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0034_auto_20190709_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='SetDefaultTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('venue', models.ForeignKey(related_name='set_default_times', to='events.Venue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
