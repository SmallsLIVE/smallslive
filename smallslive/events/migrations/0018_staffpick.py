# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_event_venue'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffPick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_picked', models.DateTimeField()),
                ('event', models.OneToOneField(related_name='staff_picked', to='events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
