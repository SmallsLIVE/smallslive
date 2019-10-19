from datetime import timedelta
from django.core.management import BaseCommand, CommandError
from django.utils import timezone

from events.models import Event, EventSet


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):

        def create_set(set_number, start, end):

            video = event.recordings.filter(set_number=set_number).filter(media_file__media_type='video').first()
            audio = event.recordings.filter(set_number=set_number).filter(media_file__media_type='audio').first()

            event_set = EventSet.objects.filter(
                event=event,
                start=start,
                end=end
            ).first()

            if not event_set:
                event_set = EventSet.objects.create(
                    event=event, start=start, end=end,
                    video_recording=video, audio_recording=audio
                )
                print 'Created Set: ', event_set.start, event_set.end
            else:
                if video:
                    event_set.video_recording=video
                if audio:
                    event_set.audio_recording=audio
                if video or audio:
                    event_set.save()
                    print 'Updated Set: ', event_set.start, event_set.end, video, audio

        for event in Event.objects.filter(venue__name='Mezzrow').order_by('-id'):
            print 'Processing event: ', event.pk

            default_timezone = timezone.get_default_timezone()
            ny_start = timezone.make_naive(event.start, default_timezone)
            print 'Start: ', ny_start
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
