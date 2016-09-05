import dj_database_url
from .local import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive',
        'USER': 'jamessam',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
    'metrics': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive-metrics',
        'USER': 'jamessam',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
}

INSTALLED_APPS += (
    'cacheops',
    'debug_toolbar',
    'hijack'
)

ENABLE_HIJACK = True

# Thumbor
THUMBOR_MEDIA_URL = 'http://127.0.0.1:8000/media/'
THUMBOR_SECURITY_KEY = 'TEST'
THUMBOR_SERVER = 'http://127.0.0.1:8888'

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
PIPELINE_ENABLED = False
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
PIPELINE_SASS_BINARY = '/Users/jamessam/venv/smallslive/bin/sassc'
PIPELINE_SASS_ARGUMENTS = ''

# disable oscar django compressor
COMPRESS_ENABLED = False

# Cache
CACHEOPS_REDIS = {
    'host': os.environ.get("REDIS_IP"),  # redis-server is on same machine
    'port': os.environ.get("REDIS_PORT"),        # default redis port
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
    'events.*': {'ops': 'all', 'timeout': 120*60},

    # And since ops is empty by default you can rewrite last line as:
    '*.*': {'timeout': 60*60},
}
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_FAKE = True

# All Auth
SITE_ID = 1
