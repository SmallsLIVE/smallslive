import os
import time
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils import timezone
from boto.s3.connection import S3Connection
from boto import elastictranscoder
from events.models import Event, Recording

PIPELINE_ID = '1430602861994-canbz1'


class Command(NoArgsCommand):
    help = 'Imports the video recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        self.bucket = conn.get_bucket("smallslivevid")
        self.transcoder = elastictranscoder.connect_to_region('us-east-1')
        self.files_transcoded = 0
        count = 0
        cutoff_date = timezone.datetime(2013, 11, 1).date()

        self.params_in = {'AspectRatio': 'auto',
                          'Container': 'auto',
                          'FrameRate': 'auto',
                          'Interlaced': 'auto',
                          'Key': '',
                          'Resolution': 'auto'}
        self.params_out = {'Key': '',
                           'PresetId': '1351620000001-000050',  # 360p preset
                           'Rotate': 'auto',
                           'ThumbnailPattern': ''}

        videos = Recording.objects.filter(media_file__media_type='video', media_file__sd_video_file="").order_by('event__start')
        for video in videos:
            original_file = str(video.media_file.file)
            folder, file = original_file.split('/')
            file_name, ext = os.path.splitext(file)
            filename_360p = os.path.join(folder, '360p', '{0}_360p{1}'.format(file_name, ext))
            thumbnail_filename = os.path.join(folder, 'thumbnails', '{0}_{{count}}'.format(file_name))
            if video.event.listing_date() < cutoff_date:
                self.params_out['PresetId'] = '1351620000001-000050'  # 360p 4:3 preset
            else:
                self.params_out['PresetId'] = '1351620000001-000040'  # 360p 16:9 preset
            self.transcode_video(original_file, filename_360p, thumbnail_filename)
            count += 1
            if count % 50 == 0:
                print count

        self.stdout.write("{0} files transcoded".format(self.files_transcoded))

    def transcode_video(self, original_filename, new_filename, thumbnail_filename):
        key = self.bucket.get_key(new_filename)
        if not key:
            self.params_in['Key'] = original_filename
            self.params_out['Key'] = new_filename
            self.params_out['ThumbnailPattern'] = thumbnail_filename
            print "TRANSCODING"
            print "----------------"
            print original_filename
            print new_filename
            print thumbnail_filename
            print self.params_out['PresetId']
            print
            self.transcoder.create_job(PIPELINE_ID, self.params_in, self.params_out)
            time.sleep(0.6)
            self.files_transcoded += 1
