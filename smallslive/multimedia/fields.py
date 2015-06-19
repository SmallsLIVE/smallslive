from django.conf import settings
from django.db import models
from .s3_storages import AudioS3Storage, VideoS3Storage


class DynamicBucketFileField(models.FileField):

    def pre_save(self, model_instance, add):
        if settings.DEBUG is False:
            if model_instance.media_type == "audio":
                storage = AudioS3Storage()
            else:
                storage = VideoS3Storage()
            model_instance.file.storage = storage
            model_instance.sd_video_file.storage = storage
        return super(DynamicBucketFileField, self).pre_save(model_instance, add)
