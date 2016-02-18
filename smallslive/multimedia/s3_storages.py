from django.conf import settings
from django.utils.deconstruct import deconstructible
from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import default_storage, get_storage_class


class ProtectedS3Storage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket_acl'] = 'private'
        kwargs['querystring_auth'] = True
        kwargs['querystring_expire'] = 60 * 120 # 2 hours
        kwargs['custom_domain'] = None
        super(ProtectedS3Storage, self).__init__(*args, **kwargs)


@deconstructible
class AudioS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = 'smallslivemp3'
        super(AudioS3Storage, self).__init__(*args, **kwargs)


class VideoS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = 'smallslivevid'
        super(VideoS3Storage, self).__init__(*args, **kwargs)

@deconstructible
class PayoutsS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = 'smallslivepayouts'
        super(PayoutsS3Storage, self).__init__(*args, **kwargs)


def get_payouts_storage_object():
    if settings.DEBUG:
        storage_class = get_storage_class()
        return storage_class()
    else:
        return PayoutsS3Storage()
