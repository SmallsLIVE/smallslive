from boto.s3.connection import OrdinaryCallingFormat, S3Connection
from django.conf import settings
from django.core.files.storage import default_storage, get_storage_class
from django.utils.deconstruct import deconstructible
from storages.backends.s3boto import S3BotoStorage


class OrdinaryConnection(S3Connection):

    def __init__(self, *args, **kargs):
        kargs['calling_format'] = OrdinaryCallingFormat()
        super(OrdinaryConnection, self).__init__(*args, **kargs)


class ProtectedS3Storage(S3BotoStorage):

    connection_class = OrdinaryConnection

    def __init__(self, *args, **kwargs):
        kwargs['bucket_acl'] = 'private'
        kwargs['querystring_auth'] = True
        kwargs['querystring_expire'] = 60 * 120 # 2 hours
        kwargs['custom_domain'] = None
        super(ProtectedS3Storage, self).__init__(*args, **kwargs)


@deconstructible
class AudioS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):

        bucket = kwargs.get('bucket', 'smallslivemp3')
        kwargs['bucket'] = bucket
        super(AudioS3Storage, self).__init__(*args, **kwargs)


class VideoS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):

        bucket = kwargs.get('bucket', 'smallslivevid')
        kwargs['bucket'] = bucket
        super(VideoS3Storage, self).__init__(*args, **kwargs)


@deconstructible
class PayoutsS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = settings.AWS_PAYOUTS_BUCKET
        super(PayoutsS3Storage, self).__init__(*args, **kwargs)


def get_payouts_storage_object():
    if settings.DEBUG:
        storage_class = get_storage_class()
        return storage_class()
    else:
        return PayoutsS3Storage()


class ImageS3Storage(ProtectedS3Storage):

    def __init__(self, *args, **kwargs):

        bucket = kwargs.get('bucket', 'smallslivestatic')
        kwargs['bucket'] = bucket

        super(ImageS3Storage, self).__init__(*args, **kwargs)

    #def url(self, name, bucket='smallslivestatic'):

    #    print  dir(self)
    #    print '*****************'
    #    print 'ImageS3Storage.url: ', bucket

    #    self._bucket = self._get_or_create_bucket(bucket)

    #    return super(ImageS3Storage, self).url(name)