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


class Event(TimeStampedModel):
    SETS = Choices(('22:00-23:00', '10-11pm'), ('23:00-0:00', '11-12pm'), ('0:00-1:00', '12-1am'))
    STATUS = Choices('Published', 'Draft', 'Cancelled')

    title = models.CharField(max_length=500)
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

    class Meta:
        ordering = ['-start']
    
    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Event, self).save(force_insert, force_update, using, update_fields)

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
        Checks if the event happened in the past.
        """
        return self.end < timezone.now()

    def get_performers(self):
        return self.artists_gig_info.select_related('artist', 'role')

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
        audio_count = self.recordings.audio().count()
        if audio_count == 0:
            status = "none"
        else:
            audio_published_count = self.recordings.all().audio().published().count()
            if audio_published_count < audio_count:
                status = "partial"
            else:
                status = "published"
        return status

    @cached_property
    def video_status(self):
        video_count = self.recordings.video().count()
        if video_count == 0:
            status = "none"
        else:
            audio_published_count = self.recordings.all().video().published().count()
            if audio_published_count < video_count:
                status = "partial"
            else:
                status = "published"
        return status

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


class RecordingManager(models.Manager.from_queryset(RecordingQuerySet)):
    use_for_related_fields = True


class Recording(models.Model):
    STATUS = Choices('Published', 'Hidden')
    FILTER_STATUS = STATUS + ['None']

    media_file = models.ForeignKey('multimedia.MediaFile', related_name='recording')
    event = models.ForeignKey(Event, related_name='recordings')
    title = models.CharField(max_length=150, blank=True)
    set_number = models.IntegerField(default=1)
    state = StatusField(default=STATUS.Published)

    objects = RecordingManager()

    class Meta:
        ordering = ['set_number']

    def is_published(self):
        return self.state == self.STATUS.Published

    def is_valid_status(self, status):
        return status in self.STATUS or status == "None"


class EventType(models.Model):
    name = models.CharField(max_length=50)
    parent = models.IntegerField()

    def __unicode__(self):
        return self.name


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

    objects = GigPlayedQuerySet.as_manager()

    class Meta:
        ordering = ['event', 'sort_order', 'is_leader']
