from django.utils.text import slugify
from django.utils.timezone import datetime, timedelta, get_default_timezone
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import QueryManager, TimeStampedModel
from tinymce import models as tinymce_models


class Event(TimeStampedModel):
    SETS = Choices(('22:00-23:00', '10-11pm'), ('23:00-0:00', '11-12pm'), ('0:00-1:00', '12-1am'))
    STATUS = Choices('Published', 'Draft', 'Cancelled', 'Hidden')

    title = models.CharField(max_length=255)
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
    performers = models.ManyToManyField('artists.Artist', through='GigPlayed', related_name='events')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    state = StatusField(default=STATUS.Draft)
    slug = models.SlugField(blank=True, max_length=150)

    objects = models.Manager()
    past = QueryManager(start__lt=datetime.now()).order_by('-start')
    upcoming = QueryManager(start__gte=datetime.now()).order_by('start')

    class Meta:
        ordering = ['-start']
    
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.id, 'slug': slugify(self.title)})

    def performers_string(self):
        "Returns the comma-separated list of performers (including the leader) as a string"
        return self.leader_string() + ", " + self.sidemen_string()

    def performers_with_instruments_string(self):
        "Returns the comma-separated list of performers with instruments (including the leader) as a string"
        return self.leader_with_instrument_string() + " // " + self.sidemen_with_instruments_string()

    def sidemen_string(self):
        "Returns the comma-separated list of sidemen (without the leader) as a string"
        performers = self.artists_gig_info.filter(is_leader=False).order_by('sort_order').select_related(
            'artist').values_list('artist__first_name', 'artist__last_name')
        # Make full names
        performers = ["{0} {1}".format(first, last) for first, last in performers]
        return ", ".join(performers)

    def sidemen_with_instruments_string(self):
        """
        Returns the comma-separated list of sidemen with instrument abbreviations
        (without the leader) as a string
        """
        performers = self.artists_gig_info.filter(is_leader=False).order_by('sort_order').select_related(
            'artist', 'role').values_list('artist__first_name', 'artist__last_name', 'role__name')
        # Make full names
        performers = ["{0} {1} ({2})".format(first, last, instrument) for first, last, instrument in performers]
        return ", ".join(performers)

    def leader_string(self):
        leader = self.artists_gig_info.filter(is_leader=True).first()
        if leader:
            text = leader.artist.full_name()
        else:
            text = ""
        return text

    def leader_with_instrument_string(self):
        leader = self.artists_gig_info.select_related('artist', 'role').filter(is_leader=True).first()
        if leader:
            text = "{0} ({1})".format(leader.artist.full_name(), leader.role.name)
        else:
            text = ""
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
        return self.artists_gig_info.prefetch_related('artist', 'role')

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
        date = self.start.date()
        if 0 <= self.start.hour <= 4:
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
            'Hidden': 'label-default',
        }
        return CSS_STATES[self.state]


class Set(models.Model):
    media_file = models.OneToOneField('multimedia.MediaFile', primary_key=True, related_name='set')
    event = models.ForeignKey(Event, related_name='sets')
    set_number = models.IntegerField(default=1)

    class Meta:
        ordering = ['set_number']


class EventType(models.Model):
    name = models.CharField(max_length=50)
    parent = models.IntegerField()

    def __unicode__(self):
        return self.name


class GigPlayed(models.Model):
    artist = models.ForeignKey('artists.Artist', related_name='gigs_played')
    event = models.ForeignKey('events.Event', related_name='artists_gig_info')
    role = models.ForeignKey('artists.Instrument')
    is_leader = models.BooleanField(default=False)
    sort_order = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ['event', 'sort_order', 'is_leader']
