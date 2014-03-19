from django.db import models


class Artist(models.Model):
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)
    salutation = models.CharField(max_length=255, blank=True)
    artist_type = models.ForeignKey('ArtistType', blank=True, null=True)
    biography = models.TextField(blank=True)
    templateid = models.IntegerField(blank=True, null=True)
    website = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['lastname']

    def __unicode__(self):
        return "{0} {1}".format(self.firstname, self.lastname)


class ArtistType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name
