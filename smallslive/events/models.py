from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=255)
    startday = models.DateField(blank=True, null=True)
    endday = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    stime = models.DateField(blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    event_type = models.ForeignKey('EventType', blank=True, null=True)
    country = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    displaytitle = models.TextField(blank=True)
    displaydescription = models.TextField(blank=True)
    extrainformation = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    donotshowartist = models.BooleanField(default=False)
    locationlink = models.TextField(blank=True)
    tickets = models.CharField(max_length=255, blank=True)
    hours = models.CharField(max_length=255, blank=True)
    datefreeform = models.TextField(blank=True)
    presenterfreeform = models.TextField(blank=True)
    extraeventtype = models.IntegerField(blank=True, null=True)
    artists_playing = models.ManyToManyField('artists.Artist', through='GigPlayed')
    
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
