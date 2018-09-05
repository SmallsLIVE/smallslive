from .local import *

SILENCED_SYSTEM_CHECKS = ["1_8.W001"]
SECRET_KEY = os.environ.get("SECRET_KEY", "herokudefault")

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
THUMBNAIL_DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive',
        'USER': 'gdelfresno',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5234',
    },
    'metrics': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive_metrics',
        'USER': 'gdelfresno',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5235',
    },
    'mezzrow': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mezzrow',
        'USER': 'gdelfresno',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5236',
    }
}

# DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
INSTALLED_APPS += (
    'cacheops',
    # 'debug_toolbar',
    'hijack',
)

ENABLE_HIJACK = True

# Thumbor
THUMBOR_SECURITY_KEY = 'TEST'
THUMBOR_SERVER = 'http://192.168.0.249:9800'
# THUMBOR_SERVER = 'http://192.168.10.84:9800'
THUMBOR_MEDIA_URL = '{}/media/'.format(THUMBOR_SERVER)

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
PIPELINE_ENABLED = False
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
PIPELINE_SASS_BINARY = '/opt/venv/smallslive/bin/sassc'
PIPELINE_SASS_ARGUMENTS = ''

# disable oscar django compressor
COMPRESS_ENABLED = False

# Pipeline doesn't touch this, SASS compiled manually by gulp
PIPELINE_CSS = {
    'css': {
        'source_filenames': (
            'css/main.css',
        ),
        'output_filename': 'css/main.css',
    },
    'dashboard_css': {
        'source_filenames': (
            'css/dashboard.css',
        ),
        'output_filename': 'css/dashboard.css',
    },
}


# Cache
CACHEOPS_REDIS = {
    'host': 'localhost',  # redis-server is on same machine
    'port': 9736,        # default redis port
    'db': 1,             # SELECT non-default redis database
                         # using separate redis db or redis instance
                         # is highly recommended

    'socket_timeout': 10,   # connection timeout in seconds, optional
}

CACHEOPS = {
    # Automatically cache any User.objects.get() calls for 15 minutes
    # This includes request.user or post.author access,
    # where Post.author is a foreign key to auth.User
    'auth.user': {'ops': 'get', 'timeout': 60*15},

    # Automatically cache all gets and queryset fetches
    # to other django.contrib.auth models for an hour
    'auth.*': {'ops': ('fetch', 'get'), 'timeout': 60*60},

    # Cache gets, fetches, counts and exists to Permission
    # 'all' is just an alias for ('get', 'fetch', 'count', 'exists')
    'auth.permission': {'ops': 'all', 'timeout': 60*60},

    'artists.*': {'ops': 'all', 'timeout': 15*60},
    # 'events.*': {'ops': 'all', 'timeout': 120*60},
    'events.event': {'ops': ('fetch', 'get'), 'timeout': 5*60},
    # And since ops is empty by default you can rewrite last line as:
    # '*.*': {'timeout': 60*60},
}

# CACHEOPS_LRU = True
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_FAKE = False

AWS_STORAGE_BUCKET_NAME = 'smallslivestatic'
AWS_ACCESS_KEY_ID = 'AKIAIXMP7S3HHB6NUWQQ'
AWS_SECRET_ACCESS_KEY = 'b84dKBWad6whVXLlUmcq2IKW5PE7M9UD4oB4tf1w'


STRIPE_PUBLISHABLE_KEY = STRIPE_PUBLIC_KEY = 'pk_test_PpbVl9GAeA0b3lTFyhJ6yJpd'
STRIPE_SECRET_KEY = 'sk_test_SrCBpROYG7Gn8gua98U0y4TK'
STRIPE_CURRENCY = 'USD'

MAILCHIMP_API_KEY = '2a99391bdf49dc7d65be048745270bfb-us5'
MAILCHIMP_LIST_ID = 'de8ca4ce7a'
MANDRILL_API_KEY = '4Ni8W8ctRED534O0HGinhQ'

FORCE_S3_SECURE = True
BROKER_URL = 'django://'
CELERY_ALWAYS_EAGER = True

# Metrics
METRICS_SERVER_URL = "http://localhost:9000"
