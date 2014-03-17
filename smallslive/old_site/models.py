# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Joineventeventtype(models.Model):
    joinid = models.IntegerField(db_column='joinId', primary_key=True) # Field name made lowercase.
    eventid = models.IntegerField(db_column='eventId') # Field name made lowercase.
    eventtypeid = models.IntegerField(db_column='eventTypeId') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'joinEventEventType'

class Joinmediaevent(models.Model):
    mediaid = models.ForeignKey('Tblmedia', db_column='mediaId') # Field name made lowercase.
    eventid = models.ForeignKey('Tblevent', db_column='eventId') # Field name made lowercase.
    sortorder = models.CharField(db_column='sortOrder', max_length=255, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'joinMediaEvent'

class Joinmediamediatype(models.Model):
    mediaid = models.IntegerField(db_column='mediaId') # Field name made lowercase.
    mediatypeid = models.IntegerField(db_column='mediaTypeId') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'joinMediaMediaType'

class Joinmediaperson(models.Model):
    mediaid = models.ForeignKey('Tblmedia', db_column='mediaId') # Field name made lowercase.
    personid = models.IntegerField(db_column='personId') # Field name made lowercase.
    sortorder = models.CharField(db_column='sortOrder', max_length=255, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'joinMediaPerson'

class Joinpersonevent(models.Model):
    eventid = models.ForeignKey('Tblevent', db_column='eventId') # Field name made lowercase.
    personid = models.IntegerField(db_column='personId') # Field name made lowercase.
    persontypeid = models.ForeignKey('Tblpersontype', db_column='personTypeId') # Field name made lowercase.
    sortorder = models.CharField(db_column='sortOrder', max_length=255, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'joinPersonEvent'

class Joinpersonpersontype(models.Model):
    personid = models.IntegerField(db_column='personId') # Field name made lowercase.
    persontypeid = models.IntegerField(db_column='personTypeId') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'joinPersonPersonType'

class Tblevent(models.Model):
    eventid = models.IntegerField(db_column='eventId', primary_key=True) # Field name made lowercase.
    title = models.CharField(max_length=255, blank=True)
    startday = models.DateField(db_column='startDay', blank=True, null=True) # Field name made lowercase.
    endday = models.DateField(db_column='endDay', blank=True, null=True) # Field name made lowercase.
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    stime = models.DateField(db_column='sTime', blank=True, null=True) # Field name made lowercase.
    subtitle = models.CharField(db_column='subTitle', max_length=255, blank=True) # Field name made lowercase.
    address = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    eventtype = models.ForeignKey('Tbleventtypes', db_column='eventType', blank=True, null=True) # Field name made lowercase.
    country = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    displaytitle = models.TextField(db_column='displayTitle', blank=True) # Field name made lowercase.
    displaydescription = models.TextField(db_column='displayDescription', blank=True) # Field name made lowercase.
    extrainformation = models.TextField(db_column='extraInformation', blank=True) # Field name made lowercase.
    active = models.BooleanField()
    donotshowartist = models.BooleanField(db_column='doNotShowArtist') # Field name made lowercase.
    locationlink = models.TextField(db_column='locationLink', blank=True) # Field name made lowercase.
    tickets = models.CharField(max_length=255, blank=True)
    hours = models.CharField(max_length=255, blank=True)
    datefreeform = models.TextField(db_column='dateFreeForm', blank=True) # Field name made lowercase.
    presenterfreeform = models.TextField(db_column='presenterFreeForm', blank=True) # Field name made lowercase.
    extraeventtype = models.IntegerField(db_column='extraEventType', blank=True, null=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'tblEvent'

class Tbleventtypes(models.Model):
    eventtypeid = models.IntegerField(db_column='eventTypeId', primary_key=True) # Field name made lowercase.
    eventtype = models.CharField(db_column='eventType', max_length=50, blank=True) # Field name made lowercase.
    eventtypeparent = models.IntegerField(db_column='eventTypeParent') # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'tblEventTypes'

class Tblmedia(models.Model):
    mediaid = models.IntegerField(db_column='mediaId', primary_key=True) # Field name made lowercase.
    medianame = models.CharField(db_column='mediaName', max_length=255, blank=True) # Field name made lowercase.
    mediapath = models.CharField(db_column='mediaPath', max_length=255, blank=True) # Field name made lowercase.
    mediatypeid = models.IntegerField(db_column='mediaTypeId', blank=True, null=True) # Field name made lowercase.
    filename = models.CharField(db_column='fileName', max_length=255, blank=True) # Field name made lowercase.
    description = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'tblMedia'

class Tblmediatype(models.Model):
    mediatypeid = models.IntegerField(db_column='mediaTypeId', primary_key=True) # Field name made lowercase.
    mediatype = models.CharField(db_column='mediaType', max_length=255, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'tblMediaType'

class Tblperson(models.Model):
    personid = models.IntegerField(db_column='personId', primary_key=True) # Field name made lowercase.
    firstname = models.CharField(db_column='firstName', max_length=255, blank=True) # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=255, blank=True) # Field name made lowercase.
    salutation = models.CharField(max_length=255, blank=True)
    persontypeid = models.ForeignKey('Tblpersontype', db_column='personTypeId', blank=True, null=True) # Field name made lowercase.
    biography = models.TextField(blank=True)
    templateid = models.IntegerField(db_column='templateId', blank=True, null=True) # Field name made lowercase.
    website = models.CharField(max_length=255, blank=True)
    class Meta:
        managed = False
        db_table = 'tblPerson'

class Tblpersontype(models.Model):
    persontypeid = models.IntegerField(db_column='personTypeId', primary_key=True) # Field name made lowercase.
    persontype = models.CharField(db_column='personType', max_length=255, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'tblPersonType'
