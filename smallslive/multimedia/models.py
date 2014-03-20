from django.db import models


class Media(models.Model):
    name = models.CharField(db_column='mediaName', max_length=255, blank=True)
    path = models.CharField(db_column='mediaPath', max_length=255, blank=True)
    media_type = models.ForeignKey('MediaType', blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)


class MediaType(models.Model):
    type = models.CharField(db_column='mediaType', max_length=255)
