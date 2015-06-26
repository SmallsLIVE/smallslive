import dj_database_url
from .local import *
import os


SECRET_KEY = os.environ.get("SECRET_KEY", "herokudefault")

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
THUMBNAIL_DEBUG = True

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config()

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


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
