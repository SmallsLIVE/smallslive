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

    def create_set(set_number, start, end):

        video = event.recordings.filter(set_number=set_number).filter(media_file__media_type='video').first()
        audio = event.recordings.filter(set_number=set_number).filter(media_file__media_type='audio').first()

        event_set = EventSet.objects.create(
            event=event, start=start, end=end,
            video_recording=video, audio_recording=audio
        )

        print('Created Set: ', event_set.start, event_set.end)

    process_count = 0
    for event in Event.objects.order_by('-id'):
        process_count += 1
        print('Processing event: ', event.pk, process_count)
        default_timezone = timezone.get_default_timezone()
        ny_start = timezone.make_naive(event.start, default_timezone)
        print('Start: ', ny_start)
        event.date = ny_start.date()
        event.save()

        first_set_start = ny_start.time()
        if 1 <= first_set_start.hour <= 5:
            # After hours: only one 3 hour set.
            first_set_end = (ny_start + timedelta(hours=3)).time()
            create_set(1, first_set_start, first_set_end)

        else:
            # Regular hours, 2 sets (1 h + break 30 mins + 1 h)
            first_set_end = (ny_start + timedelta(hours=1)).time()
            create_set(1, first_set_start, first_set_end)

            second_set_start = (ny_start + timedelta(hours=1, minutes=30)).time()
            second_set_end = (ny_start + timedelta(hours=2, minutes=30)).time()
            create_set(2, second_set_start, second_set_end)


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
                ('audio_recording', models.OneToOneField(related_name='set_is_audio',  on_delete=models.SET_NULL, null=True, blank=True, to='events.Recording')),
                ('event', models.ForeignKey(related_name='sets', on_delete=models.SET_NULL, to='events.Event')),
                ('video_recording', models.OneToOneField(related_name='set_is_video',  on_delete=models.SET_NULL, null=True, blank=True, to='events.Recording')),
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
