import os
from django.db import models
from model_utils import Choices
from .fields import DynamicBucketFileField
from .s3_storages import AudioS3Storage, VideoS3Storage


def media_file_path(instance, filename):
    if instance.category == MediaFile.CATEGORY.set:
        return '/'
    elif instance.category == MediaFile.CATEGORY.track:
        return 'tracks/'
    else:
        return 'track_previews/'


class MediaFile(models.Model):
    CATEGORY = Choices('set', 'track', 'preview')
    MEDIA_TYPE = Choices('video', 'audio')
    AUDIO_FORMATS = Choices('mp3', 'flac', 'wav', 'ogg')
    VIDEO_FORMATS = Choices('mp4', 'mpg', 'avi', 'mkv', 'mov', 'mpeg', 'flv', 'm4v')
    FORMATS = AUDIO_FORMATS + VIDEO_FORMATS

    category = models.CharField(max_length=10, choices=CATEGORY, editable=False, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE, editable=False)
    format = models.CharField(max_length=4, choices=FORMATS, editable=False)
    file = DynamicBucketFileField(upload_to=media_file_path)
    size = models.BigIntegerField(help_text="File size in bytes", default=0)
    sd_video_file = DynamicBucketFileField(blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.format = os.path.splitext(str(self.file))[1].lower().replace('.', '')
        if not self.media_type:
            if self.format in self.AUDIO_FORMATS:
                self.media_type = 'audio'
            else:
                self.media_type = 'video'
        super(MediaFile, self).save()

    def get_file_url(self):
        if self.media_type == 'audio':
            self.file.storage = AudioS3Storage()
        else:
            self.file.storage = VideoS3Storage()
        return self.file.url

    def get_sd_video_url(self):
        if self.media_type == 'audio':
            self.sd_video_file.storage = AudioS3Storage()
        else:
            self.sd_video_file.storage = VideoS3Storage()
        return self.sd_video_file.url


class Media(models.Model):
    name = models.CharField(db_column='mediaName', max_length=255, blank=True)
    path = models.CharField(db_column='mediaPath', max_length=255, blank=True)
    media_type = models.ForeignKey('MediaType', blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)


class MediaType(models.Model):
    type = models.CharField(db_column='mediaType', max_length=255)
