from django.core.urlresolvers import reverse
from django.db import models


class Artist(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    salutation = models.CharField(max_length=255, blank=True)
    artist_type = models.ForeignKey('ArtistType', blank=True, null=True)
    biography = models.TextField(blank=True)
    website = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='artist_images', max_length=150, blank=True)

    class Meta:
        ordering = ['last_name']

    def __unicode__(self):
        return u"{0} {1}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'pk': self.pk})


class ArtistType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name
