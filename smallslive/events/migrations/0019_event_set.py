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

        video_1 = event.recordings.filter(set_number=1).filter(media_file__media_type='video').first()
        audio_1 = event.recordings.filter(set_number=1).filter(media_file__media_type='audio').first()
        EventSet.objects.create(
            event=event, start=first_set_start, end=first_set_end,
            video_recording=video_1, audio_recording=audio_1
        )

        video_2 = event.recordings.filter(set_number=2).filter(media_file__media_type='video').first()
        audio_2 = event.recordings.filter(set_number=2).filter(media_file__media_type='audio').first()
        EventSet.objects.create(
            event=event, start=second_set_start, end=second_set_end,
            video_recording=video_2, audio_recording=audio_2
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
                ('audio_recording', models.OneToOneField(related_name='set_is_audio', null=True, blank=True, to='events.Recording')),
                ('event', models.ForeignKey(related_name='sets', to='events.Event')),
                ('video_recording', models.OneToOneField(related_name='set_is_video', null=True, blank=True, to='events.Recording')),
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
