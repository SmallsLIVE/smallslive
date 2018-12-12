# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0027_event_start_streaming_before_minutes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowDefaultTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_set', models.TimeField()),
                ('second_set', models.TimeField()),
                ('set_duration', models.IntegerField(default=1)),
                ('title', models.CharField(default=b'Set duration', max_length=100)),
                ('venue', models.ForeignKey(to='events.Venue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
