from django.conf import settings
from django.core.management.base import NoArgsCommand
from boto.s3.connection import S3Connection
from events.models import Event, Set
from multimedia.models import MediaFile


class Command(NoArgsCommand):
    help = 'Migrates the data from the old site to new models'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket("smallsliveaudio")
        files_imported = 0
        for event in Event.objects.filter(id__in=(6341, 6331, 6116)):
            for set_num in range(1, 7):
                filename = '{0}-{1}.mp3'.format(event.id, set_num)
                if bucket.get_key(filename):
                    try:
                        set = Set.objects.get(event_id=event.id, set_number=set_num)
                    except Set.DoesNotExist:
                        set = Set(event_id=event.id, set_number=set_num)
                    if not set.media_file_id:
                        media_file = MediaFile.objects.create(media_type="audio", file=filename)
                        set.media_file = media_file
                        set.save()
                        files_imported += 1

        self.stdout.write("{0} files imported".format(files_imported))
