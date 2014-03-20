from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=255)
    startday = models.DateField(blank=True, null=True)
    endday = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    event_type = models.ForeignKey('EventType', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=False)
    datefreeform = models.TextField(blank=True)
    artists_playing = models.ManyToManyField('artists.Artist', through='GigPlayed')

    class Meta:
        ordering = ['-startday']
    
    def __unicode__(self):
        return self.title


class EventType(models.Model):
    name = models.CharField(max_length=50)
    parent = models.IntegerField()

    def __unicode__(self):
        return self.name


class GigPlayed(models.Model):
    artist = models.ForeignKey('artists.Artist', related_name='gigs_played')
    event = models.ForeignKey('events.Event', related_name='artists_gig_info')
    role = models.ForeignKey('artists.ArtistType')
    sort_order = models.CharField(max_length=30, blank=True)
