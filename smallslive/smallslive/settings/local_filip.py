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

ALLOWED_HOSTS = ['*']
PIPELINE_ENABLED = False

# Compiled by pipeline
# PIPELINE_CSS = {
#     'css': {
#         'source_filenames': (
#             'sass/application.scss',
#         ),
#         'output_filename': 'css/application.css',
#     },
# }

# Pipeline doesn't touch this, SASS compiled manually by gulp
PIPELINE_CSS = {
    'css': {
        'source_filenames': (
            'css/application.css',
        ),
        'output_filename': 'css/application.css',
    },
}