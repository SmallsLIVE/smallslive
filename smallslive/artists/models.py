from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from sortedm2m.fields import SortedManyToManyField


class Artist(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    salutation = models.CharField(max_length=255, blank=True)
    instruments = SortedManyToManyField('Instrument', blank=True)
    biography = models.TextField(blank=True)
    website = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='artist_images', max_length=150, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='artist', blank=True, null=True)

    class Meta:
        ordering = ['last_name']

    def __unicode__(self):
        return u"{0} {1}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'pk': self.pk})

    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)


class Instrument(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name
