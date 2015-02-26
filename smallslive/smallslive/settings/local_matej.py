import os
from .base import *
import dj_database_url


SECRET_KEY = os.environ.get("SECRET_KEY", "herokudefault")

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config()

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
PIPELINE_ENABLED = False
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
}
