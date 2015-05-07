from django.conf import settings
from django.core.management.base import NoArgsCommand
from boto.s3.connection import S3Connection
from events.models import Event, Recording
from multimedia.models import MediaFile


class Command(NoArgsCommand):
    help = 'Imports the audio recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket("smallslivemp3")
        new_files_imported = 0
        files_updated = 0
        for event in Event.objects.all():
            for set_num in range(1, 7):
                filename = '{0.year}-{0.month:02}-{0.day:02}/{1}-{2}.mp3'.format(
                    event.listing_date(), event.id, set_num)
                key = bucket.get_key(filename)
                if key:
                    print filename
                    try:
                        recording = Recording.objects.get(event_id=event.id, set_number=set_num,
                                                          media_file__media_type='audio')
                    except Recording.DoesNotExist:
                        recording = Recording(event_id=event.id, set_number=set_num)
                    if not recording.media_file_id:
                        media_file, created = MediaFile.objects.get_or_create(media_type="audio", file=filename, size=key.size)
                        recording.media_file = media_file
                        recording.save()
                        new_files_imported += 1
                    else:
                        recording.media_file.file = filename
                        recording.media_file.size = key.size
                        recording.media_file.save()

        self.stdout.write("{0} new files imported".format(new_files_imported))
        self.stdout.write("{0} files updated".format(files_updated))
