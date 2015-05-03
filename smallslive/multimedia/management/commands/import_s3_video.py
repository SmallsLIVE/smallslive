from datetime import timedelta
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils import timezone
from boto.s3.connection import S3Connection
from events.models import Event, Recording
from multimedia.models import MediaFile


class Command(NoArgsCommand):
    help = 'Imports the video recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        self.bucket = conn.get_bucket("smallslivevid")
        self.files_imported = 0
        count = 0
        videos_start = timezone.datetime(year=2014, month=8, day=24)
        for event in Event.objects.filter(start__gte=videos_start).order_by('start'):
            for set_num in range(1, 7):
                filename = '{0.year}-{0.month:02}-{0.day:02}/{1}-{2}.mp4'.format(event.listing_date(), event.id, set_num)
                self.import_file(filename, event, set_num)
                count += 1
                if count % 50 == 0:
                    print count

        self.stdout.write("{0} files imported".format(self.files_imported))

    def import_file(self, filename, event, set_num):
        key = self.bucket.get_key(filename)
        if key:
            try:
                recording = Recording.objects.get(event_id=event.id, set_number=set_num,
                                                  media_file__media_type='video')
            except Recording.DoesNotExist:
                recording = Recording(event_id=event.id, set_number=set_num)
            if not recording.media_file_id:
                media_file, created = MediaFile.objects.get_or_create(media_type="video", file=filename, size=key.size)
                recording.media_file = media_file
                recording.save()
                print "{0} imported".format(filename)
                self.files_imported += 1
