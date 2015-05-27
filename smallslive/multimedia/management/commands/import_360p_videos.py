import os
from django.conf import settings
from django.core.management.base import NoArgsCommand
from boto.s3.connection import S3Connection
from events.models import Recording


class Command(NoArgsCommand):
    help = 'Imports the video recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        self.bucket = conn.get_bucket("smallslivevid")
        self.files_imported = 0
        count = 0
        for video in Recording.objects.video().filter(media_file__sd_video_file=""):
            original_file = str(video.media_file.file)
            folder, file = original_file.split('/')
            file_name, ext = os.path.splitext(file)
            filename_360p = os.path.join(folder, '360p', '{0}_360p{1}'.format(file_name, ext))
            key = self.bucket.get_key(filename_360p)
            if key:
                print "Importing {0}".format(filename_360p)
                video.media_file.sd_video_file = filename_360p
                video.media_file.save()
                count += 1

        self.stdout.write("{0} files imported".format(self.files_imported))
