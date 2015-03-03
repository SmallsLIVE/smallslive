from .local import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive',
        'USER': 'bezidejni',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
    'old': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive_old',
        'USER': 'bezidejni',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

INSTALLED_APPS += (
    'debug_toolbar',
)

COMPRESS_ENABLED = False
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Thumbor
THUMBOR_MEDIA_URL = 'http://127.0.0.1:8000/media/'
THUMBOR_SECURITY_KEY = 'TEST'
THUMBOR_SERVER = 'http://127.0.0.1:8888'

# Haystack elasticsearch backend
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.59.103:9200/',
        'INDEX_NAME': 'haystack',
    },
}

ALLOWED_HOSTS = ['*']
# Static asset configuration
PIPELINE_ENABLED = False
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
PIPELINE_SASS_BINARY = '/Users/bezidejni/.virtualenvs/smallslive/bin/sassc'
PIPELINE_SASS_ARGUMENTS = ''

# Compiled by pipeline
# PIPELINE_CSS = {
#     'css': {
#         'source_filenames': (
#             'sass/main.scss',
#         ),
#         'output_filename': 'css/application.css',
#     },
# }

# Pipeline doesn't touch this, SASS compiled manually by gulp
PIPELINE_CSS = {
    'css': {
        'source_filenames': (
            'css/main.css',
        ),
        'output_filename': 'css/main.css',
    },
}