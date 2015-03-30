from django.conf import settings
from django.core.management.base import NoArgsCommand
from boto.s3.connection import S3Connection
from events.models import Event, Recording
from multimedia.models import MediaFile


class Command(NoArgsCommand):
    help = 'Imports the audio recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket("smallsliveaudio")
        files_imported = 0
        for event in Event.objects.all():
            for set_num in range(1, 7):
                filename = '{0}-{1}.mp3'.format(event.id, set_num)
                print filename
                key = bucket.get_key(filename)
                if key:
                    try:
                        recording = Recording.objects.get(event_id=event.id, set_number=set_num)
                    except Recording.DoesNotExist:
                        recording = Recording(event_id=event.id, set_number=set_num)
                    if not recording.media_file_id:
                        media_file = MediaFile.objects.create(media_type="audio", file=filename, size=key.size)
                        recording.media_file = media_file
                        recording.save()
                        files_imported += 1

        self.stdout.write("{0} files imported".format(files_imported))
