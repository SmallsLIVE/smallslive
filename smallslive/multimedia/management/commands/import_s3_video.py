import boto
import datetime
import logging
from optparse import make_option
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Recording, Event
from multimedia.models import MediaFile

logger = logging.getLogger('cron')


class Command(BaseCommand):
    help = 'Imports the newly added video files from S3 and assigns them to correct events'

    option_list = BaseCommand.option_list + (
        make_option('--bucket-name',
                    action='store',
                    dest='bucket_name',
                    default='smallslivevid',
                    help='Bucket name'),
        make_option('--venue-name',
                    action='store',
                    dest='venue_name',
                    default='Smalls',
                    help='Venue name'),
        make_option('--full',
                    action='store_true',
                    dest='full',
                    default=False,
                    help='Import full recordings'),
        make_option('--different-source',
                    action='store_true',
                    dest='different_source',
                    default=False,
                    help='Import recording from different event ids'),

    )

    def handle(self, *args, **options):

        bucket_name = options.get('bucket_name')
        venue_name = options.get('venue_name')
        full = options.get('full')
        different_source = options.get('different_source')

        env = os.environ.get('CRON_ENV')
        now = timezone.now()
        # heroku scheduler launches the task every day, we make sure it only really does the import
        # twice a week
        if not full and env == "heroku" and now.weekday() in (0, 1, 3, 4, 5):
            logger.info('Today is not importing day')
            return

        conn = boto.connect_s3(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                               calling_format=boto.s3.connection.OrdinaryCallingFormat())


        self.bucket = conn.get_bucket(bucket_name)
        self.files_imported = 0

        if full:
            filter_cond = {}
        else:
            if len(args) == 2:
                month, year = int(args[0]), int(args[1])
                start_date = timezone.make_aware(timezone.datetime(year, month, 1), timezone.get_current_timezone())
            else:
                start_date = now - datetime.timedelta(days=30)

            filter_cond = {'start__gte': start_date, 'start__lte': now}

        if venue_name:
            filter_cond['venue__name'] = venue_name

        count = Event.objects.filter(**filter_cond).count()
        for event in Event.objects.filter(**filter_cond).order_by('start'):
            print count
            count -= 1

            if different_source:
                event_id = event.original_id
            else:
                event_id = event.id

            # Retrieve sets in the right order
            event_sets = sorted(list(event.sets.all()), Event.sets_order)
            print event_sets

            for set_num in range(1, 7):
                filename = '{0.year}-{0.month:02}-{0.day:02}/360p/{1}-{2}_360p.mp4'.format(
                    event.listing_date(), event_id, set_num)
                key = self.bucket.get_key(filename)
                if key:
                    print "importing {0}".format(filename)
                    try:
                        recording = Recording.objects.get(event_id=event.id,
                                                          set_number=set_num,
                                                          media_file__category='set',
                                                          media_file__media_type='video')
                    except Recording.DoesNotExist:
                        recording = Recording(event_id=event.id, set_number=set_num)
                    if not recording.media_file_id:
                        media_file, created = MediaFile.objects.get_or_create(category='set',
                                                                              media_type='video',
                                                                              sd_video_file=filename,
                                                                              size=key.size)
                        print 'Created: ', created
                        recording.media_file = media_file
                        recording.save()

                        self.files_imported += 1

                    if len(event_sets) >= set_num:
                        event_set = event_sets[set_num - 1]
                        event_set.video_recording = recording
                        event_set.save()
                        print 'Saved: ', event_set

        self.stdout.write("{0} new files imported".format(self.files_imported))
