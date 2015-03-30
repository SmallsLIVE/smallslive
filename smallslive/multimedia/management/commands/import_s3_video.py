from datetime import timedelta
from django.conf import settings
from django.core.management.base import NoArgsCommand
from boto.s3.connection import S3Connection
from events.models import Event, Recording
from multimedia.models import MediaFile


class Command(NoArgsCommand):
    help = 'Imports the video recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket("smallslivevid")
        files_imported = 0
        count = 0
        for event in Event.objects.all():
            for set_num in range(1, 7):
                filename = '{0.year}-{0.month}-{0.day}/{1}-{2}.mp4'.format(event.listing_date()+timedelta(days=1), event.id, set_num)
                print filename
                key = bucket.get_key(filename)
                if key:
                    try:
                        recording = Recording.objects.get(event_id=event.id, set_number=set_num,
                                                          media_file__media_type='video')
                    except Recording.DoesNotExist:
                        recording = Recording(event_id=event.id, set_number=set_num)
                    if not recording.media_file_id:
                        media_file = MediaFile.objects.create(media_type="video", file=filename, size=key.size)
                        recording.media_file = media_file
                        recording.save()
                        files_imported += 1

                count += 1
                if count % 500 == 0:
                    print count

        self.stdout.write("{0} files imported".format(files_imported))
