import pytz
import time
import functools
from cryptography.fernet import Fernet
from django.core.cache import cache
from django.db.models import Count, Max, Q, Sum
from django.conf import settings
from django.core.files.base import File
from django.urls import reverse
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta, get_default_timezone
from django.utils import six, timezone
from django.utils.functional import cached_property
from image_cropping import ImageRatioField
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import QueryManager, TimeStampedModel
from tinymce import models as tinymce_models
from multimedia.s3_storages import ImageS3Storage
from metrics.models import UserVideoMetric
from utils.hkdf import derive_fernet_key


RANGE_YEAR = 'year'
RANGE_MONTH = 'month'
RANGE_WEEK = 'week'


class EventQuerySet(models.QuerySet):

    def upcoming(self):
        return self.filter(start__gte=timezone.now()).order_by('start')

    def past(self):
        return self.filter(start__lt=timezone.now()).order_by('-start')

    def public(self):
        return self.exclude(state=Event.STATUS.Draft).order_by('-start')

    def draft(self):
        return self.filter(state=Event.STATUS.Draft).order_by('-start')

    def most_popular(self):
        return self.exclude(recordings=None).annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-r_play_count')

    def most_popular_audio(self):
        return self.filter(
            recordings__media_file__media_type='audio').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-r_play_count')

    def most_popular_video(self):
        return self.filter(
            recordings__media_file__media_type='video').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-r_play_count')

    def most_recent(self):
        return self.exclude(recordings=None).annotate(r_play_count=Count('recordings__view_count'),
                                                      added=Max('recordings__date_added')).order_by('-added')

    def most_recent_audio(self):
        return self.filter(
            recordings__media_file__media_type='audio').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-added')

    def most_recent_video(self):
        return self.filter(
            recordings__media_file__media_type='video').annotate(
            r_play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-added')

    def recently_added(self):
        return self.public().media_public().distinct().order_by('-date')

    def media_public(self):
        return self.filter(recordings__media_file__isnull=False,
                         recordings__state=Recording.STATUS.Published)

    def last_staff_picks(self):
        return self.filter(
            staff_picked__isnull=False
        ).order_by('-staff_picked__date_picked')[:15]

    def get_events_by_performers_and_artist(
            self, number_of_performers_searched, first_name=None, last_name=None, partial_name=None):

        if not first_name and not last_name and not partial_name:
            return self.annotate(num=Count('performers')).filter(Q(num=number_of_performers_searched))

        if first_name and last_name:
            return self.annotate(num=Count('performers')).filter(Q(num=number_of_performers_searched) & Q(
                        performers__first_name__iucontains=first_name) & Q(
                        performers__last_name__iucontains=last_name))
        else:
            return self.annotate(num=Count('performers')).filter(
                        Q(num=number_of_performers_searched) & Q(performers__first_name__iucontains=partial_name) |
                        Q(num=number_of_performers_searched) & Q(performers__last_name__iucontains=partial_name))

    def get_events_by_performers(self, number_of_performers_searched):
        return self.annotate(num=Count('performers')).filter(Q(num=number_of_performers_searched))

    def get_events_by_performers_and_instrument(self, number_of_performers_searched,
                                                instruments=[], all_sax_instruments=[]):

        if instruments:
            instrument = instruments[0]
            condition = Q(artists_gig_info__role__name__iexact=instrument)
            for instrument in instruments[1:]:
                condition |= Q(artists_gig_info__role__name__iexact=instrument)
            sqs = self.annotate(num=Count('performers')).filter(Q(num=number_of_performers_searched) & condition)
        else:

            instrument = all_sax_instruments[0]
            condition = Q(artists_gig_info__role__name__iexact=instrument)
            for instrument in all_sax_instruments[1:]:
                condition |= Q(artists_gig_info__role__name__iexact=instrument)
            sqs = self.annotate(num=Count('performers', distinct=True)).filter(Q(num=number_of_performers_searched) & condition)

        return sqs

    # TODO Select properly
    def event_related_videos(self, event):
        query = self.exclude(state=Event.STATUS.Draft).exclude(
            recordings__isnull=True
        ).exclude(pk=event.pk)

        leader = event.leader
        total_results = 25
        if leader:
            leader_is_leader = (
                Q(artists_gig_info__is_leader=True) &
                Q(artists_gig_info__artist=leader)
            )

            events = list(
                query.filter(
                    leader_is_leader
                ).order_by('-start')[:total_results]
            )
            total_found = len(events)
            if total_found >= total_results:
                return events

            leader_is_performer = (
                Q(artists_gig_info__is_leader=False) &
                Q(artists_gig_info__artist=leader)
            )
            events += list(
                query.filter(
                    leader_is_performer
                ).exclude(
                    pk__in=[event.id for event in events]
                ).order_by('-start')[:(total_results - total_found)]
            )

            total_found = len(events)
            if total_found >= total_results:
                return events

            sideman_is_leader = (
                Q(artists_gig_info__is_leader=True) &
                Q(artists_gig_info__artist__in=event.performers.exclude(
                    pk=leader.pk
                ))
            )
            events += list(
                query.filter(
                    sideman_is_leader
                ).exclude(
                    pk__in=[event.id for event in events]
                ).order_by('-start')[:(total_results - total_found)]
            )

            return events

        return query.order_by('-start')[:total_results]

    def get_today_and_tomorrow_events(self, just_today=False, venue_id=None, is_staff=False):
        # All the complexity comes from the events after midnight being
        # considered to be the same before, but internally date is real.

        # cover one day or two
        days = 2
        if just_today:
            days = 1

        date_range_start = get_today_start()
        date_start = date_range_start - timedelta(hours=6, minutes=1)

        date_range_end = date_range_start + timedelta(days=days)
        date_end = date_range_end - timedelta(hours=6, minutes=1)

        # from 6:00 to 6:00 (date range)
        # also make sure events have not finished already. (end > now)
        filter_data = {
            'start__gte': date_start,
            'start__lte': date_end
            # 'end__lte': date_range_end
            # 'end__gte': timezone.now()
        }

        if venue_id:
            filter_data['venue_id'] = venue_id

        qs = self.filter(**filter_data)

        if not is_staff:
            qs = qs.exclude(state=Event.STATUS.Draft)

        qs = qs.order_by('start', '-venue__sort_order')

        return qs

    def get_most_popular(self, range_size=None):

        most_popular_ids = UserVideoMetric.objects.most_popular(
            range_size=range_size, count=10
        )
        most_popular = []
        for event_data in most_popular_ids:
            try:
                event = self.get(id=event_data['event_id'])
                most_popular.append(event)
            except Event.DoesNotExist:
                pass

        return most_popular

    def get_most_popular_uploaded(self, range_size=None):

        range_end = timezone.now()

        if range_size == RANGE_MONTH:
            range_start = range_end - timedelta(days=30)
        if range_size == RANGE_WEEK:
            range_start = range_end - timedelta(days=7)
        if range_size == RANGE_YEAR:
            range_start = range_end - timedelta(days=365)

        qs = Event.objects.exclude(recordings=None)
        if range_size:
            qs = qs.filter(
                date__gte=range_start,
                date__lte=range_end
            )

        qs = qs.order_by('-seconds_played')

        items = []
        for event in qs[:20]:
            items.append(event)

        return items

    def get_live(self, venue_id=None):

        filter_data = {
            'start__lte': timezone.now(),
            'end__gte': timezone.now()
        }

        if venue_id:
            filter_data['venue_id'] = venue_id

        qs = self.filter(**filter_data)
        qs = qs.exclude(state=Event.STATUS.Draft)
        qs = qs.order_by('start')

        if qs.count() == 0:
            if 'venue_id' in filter_data:
                del filter_data['venue_id']
            qs = self.filter(**filter_data)
            qs = qs.exclude(state=Event.STATUS.Draft)
            qs = qs.order_by('start')

        return list(qs)


class CustomImageFieldFile(models.fields.files.ImageFieldFile):

    def get_url(self):
        url = self.storage.url(self.name)
        url = url.split('?')[0]
        return url


class CustomFileDescriptor(models.fields.files.FileDescriptor):

    def __get__(self, instance=None, owner=None):

        # Django code
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))

        self.field.storage = get_event_media_storage(instance)

        file = instance.__dict__[self.field.name]

        # Make sure to transform storage to a Storage instance.
        if callable(self.field.storage):
            self.field.storage = self.field.storage(instance)

        # Copied from FileDescriptor
        if self.field.name in instance.__dict__:
            file = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            file = getattr(instance, str(self.field.name))

        if isinstance(file, six.string_types) or file is None:
            attr = self.field.attr_class(instance, self.field, file)
            instance.__dict__[self.field.name] = attr
        elif isinstance(file, File) and not isinstance(file, models.fields.files.FieldFile):
            file_copy = self.field.attr_class(instance, self.field, file.name)
            file_copy.file = file
            file_copy._committed = False
            instance.__dict__[self.field.name] = file_copy
        elif isinstance(file, models.fields.files.FieldFile) and not hasattr(file, 'field'):

            file.instance = instance
            file.field = self.field
            file.storage = self.field.storage

        return instance.__dict__[self.field.name]


class CustomImageField(models.ImageField):

    attr_class = CustomImageFieldFile
    descriptor_class = CustomFileDescriptor


def get_event_media_storage(instance):

    params = {}

    if instance.get_venue_name() == 'Mezzrow':
        params['access_key'] = settings.AWS_ACCESS_KEY_ID_MEZZROW
        params['secret_key'] = settings.AWS_SECRET_ACCESS_KEY_MEZZROW
        params['bucket'] = settings.AWS_STORAGE_BUCKET_NAME_MEZZROW

    # if venue object has credentials, use them
    aws_access_key_id = instance.get_aws_access_key_id()
    aws_secret_access_key = instance.get_aws_secret_access_key()
    aws_storage_bucket_name = instance.get_aws_storage_bucket_name()
    if aws_access_key_id and \
            aws_secret_access_key and \
            aws_storage_bucket_name:
        params['access_key'] = aws_access_key_id
        params['secret_key'] = aws_secret_access_key
        params['bucket'] = aws_storage_bucket_name

    return ImageS3Storage(**params)


class Event(TimeStampedModel):
    SETS = Choices(('22:00-23:00', '10-11pm'), ('23:00-0:00', '11-12pm'), ('0:00-1:00', '12-1am'))
    STATUS = Choices('Published', 'Draft', 'Cancelled')

    title = models.CharField(db_index=True, max_length=500)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, blank=True,
                              null=True)
    start = models.DateTimeField(db_index=True, blank=True, null=True)
    end = models.DateTimeField(db_index=True, blank=True, null=True)
    set = models.CharField(choices=SETS, blank=True, max_length=10)
    description = tinymce_models.HTMLField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    event_type = models.ForeignKey('EventType', blank=True, null=True, on_delete=models.CASCADE,)
    link = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=False)
    date_freeform = models.TextField(blank=True)
    photo = CustomImageField(upload_to='event_images', storage=get_event_media_storage, max_length=150, blank=True)
    cropping = ImageRatioField('photo', '600x360', help_text="Enable cropping", allow_fullsize=True)
    performers = models.ManyToManyField('artists.Artist', through='GigPlayed', related_name='events')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,)
    state = StatusField(choices=STATUS, default=STATUS.Draft)
    slug = models.SlugField(blank=True, max_length=500)
    tickets_url = models.URLField(null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    # Import information (Mezzrow - possibly other in the future)
    # TODO: make sure this is unique. We won't have an issue with Mezzrow events though.
    original_id = models.CharField(blank=True, max_length=4096, null=True)
    import_date = models.DateTimeField(blank=True, null=True)
    # Redundant fields from UserVideoMetrics
    # Otherwise it'd be impossible to resolve search queries.
    seconds_played = models.IntegerField(default=0)
    play_count = models.IntegerField(default=0)
    # Streaming info
    streamable = models.BooleanField(default=True)
    #not_streamable_message = models.TextField(
    #    default='This event will not be live streamed at the request of the artist')
    start_streaming_before_minutes = models.IntegerField(default=15)
    #not_yet_streaming_message = models.TextField(
    #    default='Streaming for this event will be available 15 minutes before it begins')
    # minimum amount to sponsor
    minimum_sponsorship_amount = models.IntegerField(default=600)
    sponsorship_enabled = models.BooleanField(default=False)

    # Events tickets can be assigned to the Foundation or the venue account
    # Different Stripe or PayPal account will be selected for collect payments.
    is_foundation = models.BooleanField(default=False)

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ['-start']

    def __unicode__(self):
        return u'{} - {} - {}:{}'.format(self.title, self.date, self.start, self.end)

    def get_venue_name(self):
        venue_name = None
        cache_key = 'venue_{}'.format(self.venue_id)
        cached_venue_info = cache.get(cache_key)
        if cached_venue_info:
            venue_name = cached_venue_info['venue_name']
        else:
            if self.venue:
                venue_name = self.venue.name
                venue_info = {'venue_name': venue_name}
                cache.set(cache_key, venue_info)

        return venue_name

    def get_venue(self):
        return self.venue

    def get_date(self):

        if not self.start:
            raise Exception("self.start not set")

        start_hour = timezone.localtime(self.start).hour

        # this was causing issue on midnight events
        # if start_hour <= 1:
        #     print('hereee')
        #     return (self.start - timedelta(days=1)).date()

        return self.date

    def save(self, *args, **kwargs):

        start, end = self.get_actual_start_end()

        self.start = start or self.start
        self.end = end or self.end

        if not self.start or not self.end:
            raise Exception("start and end dates not set")

        if not self.slug:
            self.slug = slugify(self.title)
        super(Event, self).save(*args, **kwargs)

    def get_actual_start_end(self):
        """ Return real NY time start and end for the event.
        """
        sets = list(self.sets.all())
        # sets = sorted(sets, Event.sets_order)
        sets = sorted(sets, key=functools.cmp_to_key(Event.sets_order))

        current_timezone = timezone.get_current_timezone()

        if not sets:
            return None, None

        ny_start = datetime.combine(self.date, sets[0].start)
        try:
            ny_start = timezone.make_aware(ny_start, timezone=current_timezone)
        except (pytz.NonExistentTimeError, pytz.AmbiguousTimeError):
            ny_start = timezone.make_aware(
                ny_start + timedelta(hours=1),
                timezone=current_timezone
            )

        ny_end = datetime.combine(self.date, sets[-1].end)
        if ny_start.hour > 6 > sets[-1].end.hour >= 0:
            ny_end = ny_end + timedelta(days=1)
        try:
            ny_end = timezone.make_aware(ny_end, timezone=current_timezone)
        except (pytz.NonExistentTimeError, pytz.AmbiguousTimeError):
            ny_end = timezone.make_aware(
                ny_end + timedelta(hours=1),
                timezone=current_timezone
            )

        # ensure start < finish
        if ny_start > ny_end:
            ny_end = ny_end + timedelta(days=1)

        return ny_start, ny_end

    def get_set_start(self, set_number):
        sets = list(self.sets.all())
        #sets = sorted(sets, Event.sets_order)
        sets = sorted(sets,  key=functools.cmp_to_key(Event.sets_order))
        return sets[set_number].start

    def get_play_total(self):
        play_total = 0

        qs = UserVideoMetric.objects.filter(event_id=self.id)
        qs = qs.values('event_id').annotate(play_count=Sum('play_count'))
        if qs.count():
            play_total = qs[0]['play_count']

        return play_total

    def get_seconds_total(self):
        seconds_total = 0
        qs = UserVideoMetric.objects.filter(event_id=self.id)
        qs = qs.values('event_id').annotate(seconds_played=Sum('seconds_played'))
        if qs.count():
            seconds_total = qs[0]['seconds_played']

        hours, remainder = divmod(seconds_total, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        return '{}:{:02d}:{:02d}'.format(hours, minutes, seconds)

    def get_set_hours_display(self):

        time_format = '%-I:%M %p'

        all_sets = self.sets.all()

        if len(all_sets) == 1:
            event_set = all_sets[0]
            return '{} - {}'.format(event_set.start.strftime(time_format),
                                    event_set.end.strftime(time_format))

        #sorted_sets = sorted(list(all_sets), Event.sets_order)
        sorted_sets = sorted(list(all_sets), key=functools.cmp_to_key(Event.sets_order))

        sets_display = ' & '.join(
            [d.start.strftime(time_format) for d in sorted_sets])

        return sets_display

    def update_metrics(self):
        qs = UserVideoMetric.objects.filter(event_id=self.pk)
        qs = qs.values('event_id')
        qs = qs.annotate(play_count=Sum('play_count'),
                         seconds_played=Sum('seconds_played'))

        data = list(qs)
        if data:
            event_data = data[0]
            self.play_count = event_data['play_count']
            self.seconds_played = event_data['seconds_played']
            self.save()

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.id, 'slug': slugify(self.title)})

    def full_title(self):
        return u"{0} {1}".format(self.title, self.subtitle)

    def get_photo_url(self):
        """Mezzrow has different buckets. S3 storage is overridden and bucket name has to be passed"""
        return self.photo.get_url()

    def performers_string(self, separator=", "):
        "Returns the comma-separated list of performers (including the leader) as a string"
        return self.leader_string() + separator + self.sidemen_string()

    def performers_with_instruments_string(self, separator=", "):
        "Returns the comma-separated list of performers with instruments (including the leader) as a string"
        return self.leader_with_instrument_string() + separator + self.sidemen_with_instruments_string()

    def sidemen_string(self, separator=", "):
        "Returns the comma-separated list of sidemen (without the leader) as a string"
        performers = self.artists_gig_info.filter(is_leader=False).order_by('sort_order').select_related(
            'artist').values_list('artist__first_name', 'artist__last_name')
        # Make full names
        performers = [u"{0} {1}".format(first, last) for first, last in performers]
        return separator.join(performers)

    def sidemen_with_instruments_string(self, separator=", "):
        """
        Returns the comma-separated list of sidemen with instrument abbreviations
        (without the leader) as a string
        """
        performers = self.artists_gig_info.filter(is_leader=False).order_by('sort_order').select_related(
            'artist', 'role').values_list('artist__first_name', 'artist__last_name', 'role__name')
        # Make full names
        performers = [u"{0} {1} ({2})".format(first, last, instrument) for first, last, instrument in performers]
        return separator.join(performers)

    def get_performer_strings(self):
        artists_info = self.artists_gig_info.all()
        artists_names = [x.artist.full_name() for x in artists_info]

        if len(artists_names) > 1:

            comma_separated_artists = ', '.join(artists_names[:-1])  # That will join all elements except the last

            return u'{} and {}'.format(comma_separated_artists, artists_names[-1])
        else:
            return artists_names[0] if artists_names else ''

    def leader_string(self):
        leader = self.artists_gig_info.filter(is_leader=True).first()
        if leader:
            text = leader.artist.full_name()
        else:
            text = u""
        return text

    def leader_with_instrument_string(self):
        leader = self.artists_gig_info.select_related('artist', 'role').filter(is_leader=True).first()
        if leader:
            text = u"{0} ({1})".format(leader.artist.full_name(), leader.role.name)
        else:
            text = u""
        return text

    def display_title(self):
        """
        Returns the event display title. If the title is defined, returns the title, otherwise it generates
        one from the performer names and their roles.
        """
        leader = self.leader_string()
        if self.title:
            display_title = self.title + " w/ " + self.performers_string()
        elif leader:
            display_title = leader + " w/ " + self.sidemen_string()
        else:
            display_title = self.sidemen_string()
        return display_title

    def display_title_with_instruments(self):
        """
        Returns the event display title. If the title is defined, returns the title, otherwise it generates
        one from the performer names and their roles.
        """
        leader = self.leader_with_instrument_string()
        if self.title:
            display_title = self.title + " w/ " + self.performers_with_instruments_string()
        elif leader:
            display_title = leader + " w/ " + self.sidemen_with_instruments_string()
        else:
            display_title = self.sidemen_with_instruments_string()
        return display_title

    @staticmethod
    def sets_order(set1, set2):

        if set1.start.hour <= 5 and set2.start.hour <= 5 or \
                set1.start.hour > 5 and set2.start.hour > 5:
            if set1.start < set2.start:
                return -1
            elif set1.start > set2.start:
                return 1
            else:
                return 0
        elif set1.start.hour <= 5:  # and set2.start.hour > 5
            return 1
        elif set2.start.hour <= 5:  # and set1.start.hour > 5
            return -1

    @staticmethod
    def events_order(event1, event2):
        if event1.date < event2.date:
            return -1
        elif event1.date > event2.date:
            return 1
        else:
            sets1 = list(event1.sets.all())
            #sets1 = sorted(sets1, Event.sets_order)
            sets1 = sorted(sets1, key=functools.cmp_to_key(Event.sets_order))
            start1 = sets1[0].start
            sets2 = list(event2.sets.all())
            #sets2 = sorted(sets2, Event.sets_order)
            sets2 = sorted(sets2, key=functools.cmp_to_key(Event.sets_order))
            start2 = sets2[0].start
            if start1.hour <= 5 and start2.hour <= 5 or start1.hour >= 5 and start2.hour >= 5:
                if start1.hour < start2.hour:
                    return -1
                elif start1.hour > start2.hour:
                    return 1
                else:  # same hour
                    if start1.minute <= start2.minute:
                        return -1
                    else:
                        return 1
            else:
                if start1.hour <= 5:
                    return 1
                else:
                    return -1

    def get_range(self):
        sets = list(self.sets.all())
        #sets = sorted(sets, Event.sets_order)
        sets = sorted(sets, key=functools.cmp_to_key(Event.sets_order))
        if sets:
            start = sets[0].start
            end = sets[-1].end
        else:
            # If no sets (should not be possible)
            # let's return  the event  time to avoid an error.
            start = datetime.time(self.start)
            end = datetime.time(self.end)

        return start, end

    @property
    def is_past(self):
        """
        Checks if the event happened in the past and already ended.
        """
        return self.end < timezone.now()

    def all_events_completed(self):
        """
        You may have an event with one or more sets at the same time as another venue.
        Do not rotate the event strip until the latest
        matching set between multiple venues is complete.
        """

        end_date = self.start + timedelta(days=1)

        events = list(Event.objects.filter(start=self.start, end__lte=end_date))
        not_finished = [x for x in events if x.end > timezone.now()]

        return len(not_finished) == 0

    @property
    def is_future(self):
        """
        Checks if the event will happen in the future and hasn't yet started.
        """
        return timezone.now() < self.start

    def is_live_or_about_to_begin(self, about_to_begin=False):
        """
        An event is live depending on start and end time.
        'about_to_begin' considers the actual start date minus X minutes (typically 15) set
        in the database as 'start_streaming_before_minutes'
        """

        start = self.start
        if about_to_begin:
            start = start - timedelta(minutes=self.start_streaming_before_minutes)

        today = timezone.now()
        today_date = today.date()

        event_datetime = timezone.localtime(start)
        event_date = event_datetime.date()
        
        if event_date == today_date and timezone.localtime(start).hour < 6:
            event_date += timedelta(days=1)
            return event_date == today_date and timezone.localtime(start) <= timezone.localtime(timezone.now()) <= timezone.localtime(self.end) + timedelta(minutes=self.start_streaming_before_minutes)
        
        if (today_date - event_date).days == 1 and timezone.localtime(start).hour < 6:
            event_date += timedelta(days=1)
            start_date = start + timedelta(days=1)
            end_date = self.end + timedelta(days=1)
            return event_date == today_date and timezone.localtime(start_date) <= timezone.localtime(timezone.now()) <= timezone.localtime(end_date) + timedelta(minutes=self.start_streaming_before_minutes)


        is_live = start <= timezone.now() <= self.end + timedelta(minutes=self.start_streaming_before_minutes)

        return is_live

    @property
    def is_draft(self):
        return self.state == Event.STATUS.Draft

    @property
    def show_streaming(self):
        return self.is_live_or_about_to_begin(about_to_begin=True) and self.streamable

    @property
    def is_live(self):
        return self.is_live_or_about_to_begin(about_to_begin=False)

    def get_live_set(self):
        sets = list(self.sets.all())
        #sets = sorted(sets, Event.sets_order)
        sets = sorted(sets, key=functools.cmp_to_key(Event.sets_order))

        local_datetime = timezone.localtime(timezone.now())
        local_date = local_datetime.date()
        local_time = local_datetime.time()

        live_set = None
        for item in sets:
            if local_date == self.date:
                if item.start < local_time < item.end:
                    live_set = item
                    break
                if item.end < item.start < local_time:
                    live_set = item
                    break

        return live_set

    def get_live_stream(self):

        # TODO: set live stream url in model field

        url = ''

        if self.get_venue_name() == 'Mezzrow':
            url = 'https://www.ustream.tv/embed/23240580?html5ui'
        elif self.get_venue_name() == 'Smalls':
            url = 'https://www.ustream.tv/embed/23240575?html5ui'

        return url

    def get_next_event(self, is_staff=False):
        next_events = list(Event.objects.get_today_and_tomorrow_events(
            venue_id=self.venue_id, is_staff=is_staff))

        # Find current event in the list and return the next one.
        next_event = None
        while next_events and not next_event:
            item = next_events.pop(0)
            if self.pk == item.pk:
                next_event = item

        next_event = next_events.pop(0) if next_events else None

        return next_event

    @property
    def is_today(self):
        day_start = get_today_start()
        day_end = day_start + timedelta(days=1)

        return day_start.date() <= self.date < day_end.date()

    def get_performers(self):
        return self.artists_gig_info.select_related('artist', 'role')

    @property
    def leader(self):
        try:
            gig_info = self.artists_gig_info.filter(is_leader=True).first()
            leader = gig_info.artist
        except (GigPlayed.DoesNotExist, AttributeError):
            leader = None
        return leader

    def comma_separated_leaders(self):
        """"""
        # TODO: remove confusion between leader and admin
        artists = []
        for item in self.artists_gig_info.filter(is_leader=True):
            artists.append(item.artist.full_name())

        return ','.join(artists)

    def listing_date(self):
        """
        Shows the listing date for an event, for instance an event that is technically
        on 3/12 at 1:00 AM has a listing date of 3/11 to be correctly grouped with other
        events under that date.
        """
        local_time = timezone.localtime(self.start)
        date = local_time.date()
        if 0 <= local_time.hour <= 4:
            date += timedelta(days=-1)

        return date

    def is_early_morning(self):
        """
        Shows the listing date for an event, for instance an event that is technically
        on 3/12 at 1:00 AM has a listing date of 3/11 to be correctly grouped with other
        events under that date.
        """
        date = self.start.date()
        listing_date = self.listing_date()
        return date != listing_date

    def status_css_class(self):
        """
        Returns the Bootstrap label CSS class for the event status (published/draft/cancelled/hidden)
        """
        CSS_STATES = {
            'Published': 'label-success',
            'Draft': 'label-warning',
            'Cancelled': 'label-danger',
        }
        return CSS_STATES[self.state]

    def is_cancelled(self):
        return self.state == self.STATUS.Cancelled

    def autocomplete_label(self):
        return self.title

    def autocomplete_sublabel(self):
        return u"{dt.month}/{dt.day}/{dt.year}".format(dt=self.start)

    def has_started(self):
        return timezone.now() > self.start

    @cached_property
    def audio_status(self):
        audio_count = self.recordings.all().audio().count()
        if audio_count == 0:
            status = "none"
        else:
            audio_published_count = self.recordings.all().audio().published().count()
            if audio_published_count == 0:
                status = "blocked"
            elif audio_published_count < audio_count:
                status = "partial"
            else:
                status = "published"
        return status

    @cached_property
    def published_videos(self):
        return self.recordings.all().video().published()

    @cached_property
    def video_status(self):
        video_count = self.recordings.all().video().count()
        if video_count == 0:
            status = "none"
        else:
            video_published_count = self.recordings.all().video().published().count()
            if video_published_count == 0:
                status = "blocked"
            elif video_published_count < video_count:
                status = "partial"
            else:
                status = "published"
        return status

    @cached_property
    def published_audio(self):
        return self.recordings.all().audio().published()

    def has_published_media(self):
        status = Recording.STATUS.Published
        condition = Q(video_recording__state=status) | Q(audio_recording__state=status)
        qs = self.sets.filter(condition)
        return qs.count() > 0

    @cached_property
    def photo_crop_box(self):
        if not self.cropping or '-' in self.cropping:
            return
        try:
            top_x, top_y, bottom_x, bottom_y = self.cropping.split(',')
            return ((int(top_x), int(top_y)), (int(bottom_x), int(bottom_y)))
        except:
            return None

    def get_sets_info_dict(self):
        sets_info = []
        #for item in sorted(list(self.sets.all()), Event.sets_order):
        sets = sorted(list(self.sets.all()), key=functools.cmp_to_key(Event.sets_order))
        for item in sets:
            info = {
                'start': item.start,
                'has_media': bool(item.audio_recording or item.video_recording)
            }
            sets_info.append(info)

        return sets_info

    def get_artists_info_dict(self):
        # DOCUMENT: Why is this necessary.
        event_artists_info = []
        for gig in self.artists_gig_info.select_related('artist', 'role'):
            event_artists_info.append({
                'name': gig.artist.full_name(),
                'role': gig.role.name,
                'absolute_url': gig.artist.get_absolute_url(),
                'leader': 'leader' if gig.is_leader else 'sideman'
            })
        return event_artists_info

    def get_tickets(self):
        tickets = []
        sets = list(self.sets.all())
        # sets = sorted(sets, Event.sets_order)
        sets = sorted(sets, key=functools.cmp_to_key(Event.sets_order))
        for event_set in sets:
            tickets += list(event_set.tickets.all())

        return tickets

    def is_public_event(self):
        public_list = self.recordings.all().published().count()
        is_public = public_list > 0

        return is_public

    def get_aws_access_key_id(self):
        aws_access_key_id = None
        cache_key = 'venue_{}_aws_access_key_id'.format(self.venue_id)
        cached_venue_aws_access_key_id = cache.get(cache_key)
        if cached_venue_aws_access_key_id:
            aws_access_key_id = cached_venue_aws_access_key_id
        else:
            if self.venue:
                aws_access_key_id = self.venue.get_aws_access_key_id
                cache.set(cache_key, aws_access_key_id)

        return aws_access_key_id

    def get_aws_secret_access_key(self):
        aws_secret_access_key = None
        cache_key = 'venue_{}_aws_secret_access_key'.format(self.venue_id)
        cached_venue_aws_secret_access_key = cache.get(cache_key)
        if cached_venue_aws_secret_access_key:
            aws_secret_access_key = cached_venue_aws_secret_access_key
        else:
            if self.venue:
                aws_secret_access_key = self.venue.get_aws_secret_access_key
                cache.set(cache_key, aws_secret_access_key)

        return aws_secret_access_key

    def get_aws_storage_bucket_name(self):
        aws_storage_bucket_name = None
        cache_key = 'venue_{}_aws_storage_bucket_name'.format(self.venue_id)
        cached_venue_aws_storage_bucket_name = cache.get(cache_key)
        if cached_venue_aws_storage_bucket_name:
            aws_storage_bucket_name = cached_venue_aws_storage_bucket_name
        else:
            if self.venue:
                aws_storage_bucket_name = self.venue.get_aws_storage_bucket_name
                cache.set(cache_key, aws_storage_bucket_name)

        return aws_storage_bucket_name


class RecordingQuerySet(models.QuerySet):
    def video(self):
        return self.filter(media_file__media_type='video')

    def audio(self):
        return self.filter(media_file__media_type='audio')

    def published(self):
        return self.filter(state=Recording.STATUS.Published)

    def hidden(self):
        return self.filter(state=Recording.STATUS.Hidden)

    def most_popular(self):
        return self.order_by('-view_count')

    def most_recent(self):
        return self.order_by('-date_added')


class RecordingManager(models.Manager.from_queryset(RecordingQuerySet)):
    use_for_related_fields = True


class Recording(models.Model):
    STATUS = Choices('Published', 'Hidden')
    FILTER_STATUS = STATUS + ['None']

    media_file = models.OneToOneField('multimedia.MediaFile', related_name='recording', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='recordings', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True)
    set_number = models.IntegerField(default=1)
    state = StatusField(choices=STATUS, default=STATUS.Published)
    date_added = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)

    objects = RecordingManager()

    class Meta:
        ordering = ['set_number']

    def __unicode__(self):
        return u'State: {}, Event: {}, Set: {}'.format(
            repr(self.state) or u'N/A',
            self.event or u'N/A',
            self.set_number or u'N/A',
        )

    def is_published(self):
        return self.state == self.STATUS.Published

    def is_valid_status(self, status):
        return status in self.STATUS or status == "None"

    def get_redirect_url(self):
        """
        Redirect view used to track media using jwplayer analytics in a way that they have a
        consistent URL and not have the S3 access key.
        """
        return reverse('media_redirect', kwargs={'recording_id': self.id})


class EventType(models.Model):
    name = models.CharField(max_length=50)
    parent = models.IntegerField()

    def __unicode__(self):
        return self.name


class EventSetManager(models.Manager):

    def with_media(self):
        return self.filter(Q(video_recording__isnull=False) | Q(audio_recording__isnull=False)).order_by('id')


class EventSet(models.Model):
    start = models.TimeField()
    end = models.TimeField(blank=True, null=True)
    event = models.ForeignKey('events.Event', related_name='sets', on_delete=models.CASCADE)
    video_recording = models.OneToOneField('events.Recording', related_name='set_is_video', blank=True, null=True,
                                           on_delete=models.CASCADE,)
    audio_recording = models.OneToOneField('events.Recording', related_name='set_is_audio', blank=True, null=True,
                                           on_delete=models.CASCADE,)
    walk_in_price = models.IntegerField(default=25)

    objects = EventSetManager()

    def __unicode__(self):
        return '{} - {}'.format(self.start, self.end)

    def save(self, *args, **kwargs):
        obj = super(EventSet, self).save(*args, **kwargs)

        # Keep actual start, end dates of the event.
        (self.event.start, self.event.end) = self.event.get_actual_start_end()
        self.event.save()

        return obj

    @property
    def has_media(self):
        return self.video_recording or self.audio_recording

    @property
    def is_past(self):
        end_date = self.event.date
        # i. e. starts at 23:00 and ends at 1:00 (ends on the next day)
        if self.start.hour > self.end.hour or self.start.hour == 0:
            end_date = end_date + timedelta(days=1)
        ny_end = datetime.combine(end_date, self.end)
        ny_end = timezone.get_current_timezone().localize(ny_end, is_dst=False)

        return ny_end <= timezone.now()

    @property
    def utc_start(self):
        real_date = self.event.date
        if 0 <= self.start.hour < 5:
            real_date = real_date + timedelta(days=1)

        ny_start = datetime.combine(real_date, self.start)
        return timezone.make_aware(ny_start, timezone=(timezone.get_current_timezone()))

    @property
    def utc_end(self):
        ny_end = datetime.combine(self.event.date, self.end)
        return timezone.make_aware(ny_end, timezone=(timezone.get_current_timezone()))

    def get_user_video_metrics_dict(self):

        audio_play_count = {}
        video_play_count = {}
        audio_seconds_played = {}
        video_seconds_played = {}

        if self.audio_recording:
            audio_metrics = UserVideoMetric.objects.filter(recording_id=self.audio_recording.pk)
            audio_seconds_played = audio_metrics.values('recording_id').annotate(seconds_played=Sum('seconds_played'))
            if audio_seconds_played:
                audio_seconds_played = audio_seconds_played[0]
            else:
                audio_seconds_played = {}
            audio_play_count = audio_metrics.values('recording_id').annotate(play_count=Sum('play_count'))
            if audio_play_count:
                audio_play_count = audio_play_count[0]
            else:
                audio_play_count = {}

        if self.video_recording:
            video_metrics = UserVideoMetric.objects.filter(recording_id=self.video_recording.pk)
            video_seconds_played = video_metrics.values('recording_id').annotate(seconds_played=Sum('seconds_played'))
            if video_seconds_played:
                video_seconds_played = video_seconds_played[0]
            else:
                video_seconds_played = {}
            video_play_count = video_metrics.values('recording_id').annotate(play_count=Sum('play_count'))
            if video_play_count:
                video_play_count = video_play_count[0]
            else:
                video_play_count = {}

        audio_seconds_played = audio_seconds_played.get('seconds_played', 0)
        video_seconds_played = video_seconds_played.get('seconds_played', 0)
        total_seconds_played = audio_seconds_played + video_seconds_played

        audio_play_count = audio_play_count.get('play_count', 0)
        video_play_count = video_play_count.get('play_count', 0)
        total_play_count = audio_play_count + video_play_count

        return {
            'seconds_played': {
                'audio': audio_seconds_played,
                'video': video_seconds_played,
                'total': total_seconds_played,
                'formatted': time.strftime('%H:%M:%S', time.gmtime(total_seconds_played))
            },
            'play_count': {
                'audio': audio_play_count,
                'video': video_play_count,
                'total': total_play_count,
            }
        }


class GigPlayedQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(event__start__gte=timezone.now()).order_by('-event__start')

    def past(self):
        return self.filter(event__start__lt=timezone.now()).order_by('event__start')


class GigPlayed(models.Model):
    artist = models.ForeignKey('artists.Artist', related_name='gigs_played', on_delete=models.CASCADE)
    event = models.ForeignKey('events.Event', related_name='artists_gig_info', on_delete=models.CASCADE)
    role = models.ForeignKey('artists.Instrument', on_delete=models.CASCADE)
    is_leader = models.BooleanField(default=False)
    sort_order = models.CharField(max_length=30, blank=True)
    is_admin = models.BooleanField(default=False)

    objects = GigPlayedQuerySet.as_manager()

    class Meta:
        ordering = ['event', 'sort_order', 'is_leader']

    def __unicode__(self):
        return u'{} - {}'.format(self.artist.full_name(), self.role.name)


class Venue(models.Model):

    name = models.CharField(max_length=100, unique=True)
    audio_bucket_name = models.CharField(max_length=4096, default='smallslivemp3')
    video_bucket_name = models.CharField(max_length=4096, default='smallslivevid')

    aws_access_key_id = models.CharField(max_length=4096, null=True)
    aws_secret_access_key = models.CharField(max_length=4096, blank=True, null=True)
    aws_storage_bucket_name = models.CharField(max_length=4096, blank=True, null=True)
    stripe_publishable_key = models.CharField(max_length=4096, blank=True, null=True)
    stripe_secret_key = models.CharField(max_length=4096, blank=True, null=True)
    paypal_client_id = models.CharField(max_length=4096, blank=True, null=True)
    paypal_client_secret = models.CharField(max_length=4096, blank=True, null=True)

    foundation = models.BooleanField(default=True)

    # Priority for sorting events
    # Higher number shows first.
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    @cached_property
    def get_name(self):
        return self.name

    @property
    def short_name(self):
        return self.name.split(' ')[0]

    @property
    def color(self):
        # TODO: un-hardcode o_o'
        if 'mezzrow' in self.name.lower():
            return 'rgb(241, 187, 83)'
        return '#D21535'

    @property
    def get_aws_access_key_id(self):
        if self.aws_access_key_id:
            return self.fernet.decrypt(force_bytes(self.aws_access_key_id)).decode('utf-8')
        return None

    @property
    def get_aws_secret_access_key(self):
        if self.aws_secret_access_key:
            return self.fernet.decrypt(force_bytes(self.aws_secret_access_key)).decode('utf-8')
        return None

    @property
    def get_aws_storage_bucket_name(self):
        if self.aws_storage_bucket_name:
            return self.fernet.decrypt(force_bytes(self.aws_storage_bucket_name)).decode('utf-8')
        return None

    @property
    def get_stripe_publishable_key(self):
        if self.stripe_publishable_key:
            return self.fernet.decrypt(force_bytes(self.stripe_publishable_key))
        return None

    @property
    def get_stripe_secret_key(self):
        if self.stripe_secret_key:
            return self.fernet.decrypt(force_bytes(self.stripe_secret_key))
        return None

    @property
    def get_paypal_client_id(self):
        if self.paypal_client_id:
            return self.fernet.decrypt(force_bytes(self.paypal_client_id))
        return None

    @property
    def get_paypal_client_secret(self):
        if self.paypal_client_secret:
            return self.fernet.decrypt(force_bytes(self.paypal_client_secret))
        return None

    @cached_property
    def fernet(self):
        return Fernet(derive_fernet_key(settings.SECRET_KEY))

    def save(self, *args, **kwargs):
        self.aws_access_key_id = self.fernet.encrypt(
            force_bytes(self.aws_access_key_id)
        )
        self.aws_secret_access_key = self.fernet.encrypt(
            force_bytes(self.aws_secret_access_key)
        )
        self.aws_storage_bucket_name = self.fernet.encrypt(
            force_bytes(self.aws_storage_bucket_name)
        )
        self.stripe_publishable_key = self.fernet.encrypt(
            force_bytes(self.stripe_publishable_key)
        )
        self.stripe_secret_key = self.fernet.encrypt(
            force_bytes(self.stripe_secret_key)
        )
        self.paypal_client_id = self.fernet.encrypt(
            force_bytes(self.paypal_client_id)
        )

        self.paypal_client_secret = self.fernet.encrypt(
            force_bytes(self.paypal_client_secret)
        )
        super(Venue, self).save(*args, **kwargs)


class ShowDefaultTime(models.Model):
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, blank=False, related_name='default_times')
    first_set = models.TimeField(blank=False)
    second_set = models.TimeField(blank=True,null=True)
    set_duration = models.IntegerField(default=1)
    title = models.CharField(max_length=100, default='Set duration')

    def sets_start(self):
        if self.second_set or self.second_set is not None:
            return self.first_set.strftime('%H:%M') + "-" + self.second_set.strftime('%H:%M')
        else:
            return self.first_set.strftime('%H:%M')

    def sets_readable_start(self):
        if self.second_set or self.second_set is not None:
            return self.first_set.strftime('%I:%M %p') + " & " + self.second_set.strftime('%I:%M %p')
        else:
            first_set_end = datetime.combine(datetime.now(), self.first_set) + timedelta(hours=self.set_duration)
            return self.first_set.strftime('%I:%M %p') + " - " + first_set_end.strftime('%I:%M %p')

    def get_venue_name(self):

        return self.venue.get_name

    def __unicode__(self):
        return self.sets_readable_start() + "    " + self.get_venue_name()


class StaffPick(models.Model):
    event = models.OneToOneField('events.Event', related_name='staff_picked', on_delete=models.CASCADE)
    date_picked = models.DateTimeField()


def get_today_start():
    """ Day actually starts at 6 am"""

    start = timezone.localtime(timezone.now())
    if start.hour < 6:
        start = start - timedelta(days=1)
    start = start.replace(hour=6, minute=0)

    return start


class Comment(models.Model):

    STATUS_APPROVED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_IN_REVIEW = 'IR'

    STATUS = (
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_IN_REVIEW, 'In Review'),
    )

    status = models.CharField(choices=STATUS, default=STATUS_APPROVED,
                              max_length=2)
    event_set = models.ForeignKey(EventSet, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    content = models.TextField(max_length=500, null=True, blank=False)

    def save(self, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        super(Comment, self).save(**kwargs)
