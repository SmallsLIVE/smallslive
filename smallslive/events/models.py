from django.db.models import Count, Max, Q
from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta, get_default_timezone
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from image_cropping import ImageRatioField
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import QueryManager, TimeStampedModel
from tinymce import models as tinymce_models


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
            play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-play_count')

    def most_popular_audio(self):
        return self.filter(
            recordings__media_file__media_type='audio').annotate(
            play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-play_count')

    def most_popular_video(self):
        return self.filter(
            recordings__media_file__media_type='video').annotate(
            play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-play_count')

    def most_recent(self):
        return self.exclude(recordings=None).annotate(play_count=Count('recordings__view_count'),
                                                      added=Max('recordings__date_added')).order_by('-added')

    def most_recent_audio(self):
        return self.filter(
            recordings__media_file__media_type='audio').annotate(
            play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-added')

    def most_recent_video(self):
        return self.filter(
            recordings__media_file__media_type='video').annotate(
            play_count=Count('recordings__view_count'), added=Max('recordings__date_added')).order_by('-added')

    def last_staff_picks(self):
        return self.filter(
            staff_picked__isnull=False
        ).order_by('-staff_picked__date_picked')

    # TODO Select properly
    def event_related_videos(self, event):
        query = self.exclude(state=Event.STATUS.Draft).exclude(
            recordings__isnull=True
        ).exclude(pk=event.pk)

        leader = event.leader
        total_results = 8
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


class Event(TimeStampedModel):
    SETS = Choices(('22:00-23:00', '10-11pm'), ('23:00-0:00', '11-12pm'), ('0:00-1:00', '12-1am'))
    STATUS = Choices('Published', 'Draft', 'Cancelled')

    title = models.CharField(max_length=500)
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE, blank=True,
                              null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    set = models.CharField(choices=SETS, blank=True, max_length=10)
    description = tinymce_models.HTMLField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    event_type = models.ForeignKey('EventType', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=False)
    date_freeform = models.TextField(blank=True)
    photo = models.ImageField(upload_to='event_images', max_length=150, blank=True)
    cropping = ImageRatioField('photo', '600x360', help_text="Enable cropping", allow_fullsize=True)
    performers = models.ManyToManyField('artists.Artist', through='GigPlayed', related_name='events')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    state = StatusField(default=STATUS.Draft)
    slug = models.SlugField(blank=True, max_length=500)

    objects = EventQuerySet.as_manager()
    #past = QueryManager(start__lt=datetime.now()).order_by('-start')
    #upcoming = QueryManager(start__gte=datetime.now()).order_by('start')
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-start']

    def __unicode__(self):
        return self.title

    def get_date(self):

        event_date = self.date

        first_set = self.sets.all()[0]
        if first_set.start.hour <= 5:
            event_date = event_date - timedelta(days=1)

        return event_date

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Event, self).save(force_insert, force_update, using, update_fields)

    def get_set_hours_display(self):

        time_format = '%-I:%M %p'

        all_sets = self.sets.all()

        print '***********'
        print self.full_title()
        print all_sets

        if len(all_sets) == 1:
            event_set = all_sets[0]
            return '{} - {}'.format(event_set.start.strftime(time_format),
                                    event_set.end.strftime(time_format))
        all_sets = list(all_sets.values_list('start', flat=True))

        def midnight_sort(x, y):
            x_stamp = x.hour * 60 + x.minute
            y_stamp = y.hour * 60 + y.minute

            if 0 <= x.hour < 6:
                x_stamp += 24 * 60

            if 0 <= y.hour < 6:
                y_stamp += 24 * 60

            return x_stamp - y_stamp

        sorted_sets = sorted(all_sets, cmp=midnight_sort)

        return ' & '.join(
            [d.strftime(time_format) for d in sorted_sets]
        )

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.id, 'slug': slugify(self.title)})

    def full_title(self):
        return u"{0} {1}".format(self.title, self.subtitle)

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

    @property
    def is_past(self):
        """
        Checks if the event happened in the past and already ended.
        """
        return self.end < timezone.now()

    @property
    def is_future(self):
        """
        Checks if the event will happen in the future and hasn't yet started.
        """
        return self.start > timezone.now()

    @property
    def is_live(self):
        return bool(self.get_live_set())

    def get_live_set(self):
        event_ny_start = None
        current_timezone = timezone.get_current_timezone()
        live_set = None
        for event_set in self.sets.all():
            # Convert set times to UTC, they are in America/New York timezone
            ny_start = datetime.combine(self.date, event_set.start)
            ny_start = timezone.make_aware(ny_start, timezone=current_timezone)
            if not event_ny_start or ny_start < event_ny_start:
                event_ny_start = ny_start

            ny_end = datetime.combine(self.date, event_set.end)
            ny_end = timezone.make_aware(ny_end, timezone=current_timezone)
            if ny_start <= timezone.localtime(timezone.now()) < ny_end:
                live_set = event_set
                break

        return live_set

    @property
    def is_today(self):
        day_start = get_today_start()
        day_end = day_start + timedelta(days=1)

        return day_start <= self.start < day_end

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

    @cached_property
    def photo_crop_box(self):
        if not self.cropping or '-' in self.cropping:
            return
        top_x, top_y, bottom_x, bottom_y = self.cropping.split(',')
        return ((top_x, top_y), (bottom_x, bottom_y))


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

    media_file = models.OneToOneField('multimedia.MediaFile', related_name='recording')
    event = models.ForeignKey(Event, related_name='recordings')
    title = models.CharField(max_length=150, blank=True)
    set_number = models.IntegerField(default=1)
    state = StatusField(default=STATUS.Published)
    date_added = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)

    objects = RecordingManager()

    class Meta:
        ordering = ['set_number']

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


class EventSet(models.Model):
    start = models.TimeField()
    end = models.TimeField(blank=True, null=True)
    event = models.ForeignKey('events.Event', related_name='sets')
    video_recording = models.OneToOneField('events.Recording', related_name='set_is_video', blank=True, null=True)
    audio_recording = models.OneToOneField('events.Recording', related_name='set_is_audio', blank=True, null=True)

    @property
    def has_media(self):
        return self.video_recording or self.audio_recording

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


class GigPlayedQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(event__start__gte=timezone.now()).order_by('-event__start')

    def past(self):
        return self.filter(event__start__lt=timezone.now()).order_by('event__start')


class GigPlayed(models.Model):
    artist = models.ForeignKey('artists.Artist', related_name='gigs_played')
    event = models.ForeignKey('events.Event', related_name='artists_gig_info')
    role = models.ForeignKey('artists.Instrument')
    is_leader = models.BooleanField(default=False)
    sort_order = models.CharField(max_length=30, blank=True)
    is_admin = models.BooleanField(default=False)

    objects = GigPlayedQuerySet.as_manager()

    class Meta:
        ordering = ['event', 'sort_order', 'is_leader']


class Venue(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class StaffPick(models.Model):
    event = models.OneToOneField('events.Event', related_name='staff_picked')
    date_picked = models.DateTimeField()


def get_today_start():
    """Assuming that before 1am NY it's still the same date as the day before."""

    now_ny = timezone.localtime(timezone.now())
    # up until 1 am the current set has the previous day's date.
    # so we need to set the start date at 10:00 pm the day before
    if now_ny.hour == 0 and now_ny.minute <= 59:
        start = now_ny - timedelta(days=1)
        start = start.replace(hour=22, minute=0)
    else:
        start = now_ny.replace(hour=5, minute=0)

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
    event_set = models.ForeignKey(EventSet, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments')
    created_at = models.DateTimeField()
    content = models.TextField(max_length=500, null=True, blank=False)

    def save(self, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        super(Comment, self).save(**kwargs)
