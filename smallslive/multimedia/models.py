import os
from django.db import models
from model_utils import Choices
from .fields import DynamicBucketFileField
from .s3_storages import AudioS3Storage, VideoS3Storage


class MediaFile(models.Model):
    MEDIA_TYPE = Choices('video', 'audio')
    AUDIO_FORMATS = Choices('mp3', 'flac', 'wav')
    VIDEO_FORMATS = Choices('mp4', 'mpg', 'avi', 'mkv', 'mov', 'mpeg', 'flv', 'm4v')
    FORMATS = AUDIO_FORMATS + VIDEO_FORMATS

    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE, editable=False)
    format = models.CharField(max_length=4, choices=FORMATS, editable=False)
    file = DynamicBucketFileField(upload_to='/')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.format = os.path.splitext(str(self.file))[1].lower()
        if self.format in self.VIDEO_FORMATS:
            self.media_type = 'video'
        else:
            self.media_type = 'audio'
        super(MediaFile, self).save()

    def get_file_url(self):
        if self.media_type == 'audio':
            self.file.storage = AudioS3Storage()
        else:
            self.file.storage = VideoS3Storage()
        return self.file.url


class Media(models.Model):
    name = models.CharField(db_column='mediaName', max_length=255, blank=True)
    path = models.CharField(db_column='mediaPath', max_length=255, blank=True)
    media_type = models.ForeignKey('MediaType', blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)


class MediaType(models.Model):
    type = models.CharField(db_column='mediaType', max_length=255)
