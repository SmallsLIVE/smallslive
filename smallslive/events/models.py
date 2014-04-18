from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.timezone import datetime
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import QueryManager, TimeStampedModel


class Event(TimeStampedModel):
    SETS = Choices('10-11pm', '11-12pm', '12-1am')
    STATUS = Choices('Draft', 'Published', 'Cancelled', 'Hidden')

    title = models.CharField(max_length=255)
    start_day = models.DateField(blank=True, null=True)
    end_day = models.DateField(blank=True, null=True)
    set = models.CharField(choices=SETS, blank=True, max_length=10)
    description = models.TextField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    event_type = models.ForeignKey('EventType', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=False)
    date_freeform = models.TextField(blank=True)
    photo = models.ImageField(upload_to='event_images', max_length=150, blank=True)
    performers = models.ManyToManyField('artists.Artist', through='GigPlayed')
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    state = StatusField()

    objects = models.Manager()
    past = QueryManager(start_day__lt=datetime.now().date()).order_by('-start_day')
    upcoming = QueryManager(start_day__gte=datetime.now().date()).order_by('start_day')

    class Meta:
        ordering = ['-start_day']
    
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.id})

    def display_title(self):
        """
        Returns the event display title. If the title is defined, returns the title, otherwise it generates
        one from the performer names and their roles.
        """
        if self.title:
            display_title = self.title
        else:
            performers = self.artists_gig_info.order_by('sort_order').select_related('artist', 'role').values_list(
                'artist__first_name', 'artist__last_name', 'role__name')
            # Make full names
            performers = [("{0} {1}".format(first, last), instrument) for first, last, instrument in performers]
            first = performers.pop(0)
            display_title = first[0]
            # If only one member, show his name, otherwise list all the remaining artists and their instruments
            if performers:
                display_title += " w/ "
                for performer in performers:
                    display_title += "{0} ({1}), ".format(performer[0], performer[1])
            display_title = display_title[:-2]
        return display_title

    def is_past(self):
        """
        Checks if the event happened in the past.
        """
        return self.end_day < datetime.now().date()


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
