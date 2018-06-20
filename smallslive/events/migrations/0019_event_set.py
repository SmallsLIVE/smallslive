# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.db import models, migrations
from django.utils import timezone


def convert_to_event_set(apps, schema_editor):
    # noinspection PyPep8Naming
    Event = apps.get_model('events', 'Event')
    # noinspection PyPep8Naming
    EventSet = apps.get_model('events', 'EventSet')

    for event in Event.objects.all():
        default_timezone = timezone.get_default_timezone()
        ny_start = timezone.make_naive(event.start, default_timezone)
        ny_end = timezone.make_naive(event.end, default_timezone)
        event.date = ny_start.date()
        event.save()

        first_set_start = ny_start.time()
        second_set_start = ny_end.time()

        first_set_end = (ny_start + timedelta(hours=1)).time()
        second_set_end = (ny_end + timedelta(hours=1)).time()

        recording_1 = event.recordings.filter(set_number=1).first()
        EventSet.objects.create(
            event=event, start=first_set_start, end=first_set_end, recording=recording_1
        )

        recording_2 = event.recordings.filter(set_number=2).first()
        EventSet.objects.create(
            event=event, start=second_set_start, end=second_set_end, recording=recording_2
        )


def dummy(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_staffpick'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.TimeField()),
                ('end', models.TimeField(null=True, blank=True)),
                ('event', models.ForeignKey(related_name='sets', to='events.Event')),
                ('recording', models.OneToOneField(related_name='set', null=True, blank=True, to='events.Recording')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(convert_to_event_set, dummy)
    ]
