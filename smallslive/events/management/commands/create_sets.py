from datetime import timedelta
from django.core.management import BaseCommand, CommandError
from django.utils import timezone

from events.models import Event, EventSet


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):

        count = 0
        for event in Event.objects.filter(venue__name='Mezzrow'):
            count += 1
            if event.sets.all().count() > 0:
                print 'Skipping'
                continue

            print 'Processing: {}'.format(count)
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
