import os
from django.conf import settings
from django.core.management.base import NoArgsCommand
from boto.s3.connection import S3Connection
from events.models import Event, Recording


class Command(NoArgsCommand):
    help = 'Imports the video recordings from S3 and assigns them to correct events'

    def handle_noargs(self, *args, **options):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        old_bucket_name = "smallsliveaudio"
        old_bucket = conn.get_bucket(old_bucket_name)
        new_bucket_name = "smallslivemp3"
        new_bucket = conn.get_bucket(new_bucket_name)
        count = 0

        files = old_bucket.get_all_keys()
        for file in files:
            name, ext = os.path.splitext(file.key)
            event_id, set_num = name.split('-')
            try:
                # if event found, copy using the proper naming scheme
                event = Event.objects.get(id=event_id)
                filename = '{0.year}-{0.month:02}-{0.day:02}/{1}-{2}{3}'.format(
                    event.listing_date(), event.id, set_num, ext)

            except Event.DoesNotExist:
                # if there's no event in the DB, just copy the file as is
                filename = file.key

            if not new_bucket.get_key(filename):
                print "Will copy {0}".format(filename)
                new_bucket.copy_key(filename, old_bucket_name, file.key)
                count += 1

            # if new_bucket.get_key(filename):
            #     old_bucket.delete_key(file.key)

        self.stdout.write("{0} files copied".format(count))
