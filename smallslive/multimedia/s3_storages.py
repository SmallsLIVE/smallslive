from storages.backends.s3boto import S3BotoStorage


class ProtectedS3Storage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket_acl'] = 'private'
        kwargs['querystring_auth'] = True
        kwargs['querystring_expire'] = 600
        kwargs['custom_domain'] = None
        super(ProtectedS3Storage, self).__init__(*args, **kwargs)


class AudioS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = 'smallsliveaudio'
        super(AudioS3Storage, self).__init__(*args, **kwargs)


class VideoS3Storage(ProtectedS3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = 'smallslivevideo'
        super(VideoS3Storage, self).__init__(*args, **kwargs)
