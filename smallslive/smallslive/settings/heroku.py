import os
from .base import *
import dj_database_url


def env_var(key, default=None):
    """Retrieves env vars and makes Python boolean replacements"""
    val = os.environ.get(key, default)
    if val == 'True':
        val = True
    elif val == 'False':
        val = False
    return val

DEBUG = env_var("DEBUG", False)
TEMPLATE_DEBUG = env_var("DEBUG", False)

SECRET_KEY = os.environ.get("SECRET_KEY", "herokudefault")

# Parse database configuration from $DATABASE_URL
DATABASES['default'] = dj_database_url.config()
DATABASES['metrics'] = dj_database_url.config('HEROKU_POSTGRESQL_PINK_URL')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
STATICFILES_STORAGE = "utils.storages.GzipManifestPipelineStorage"
PIPELINE_SASS_BINARY = 'sassc'
PIPELINE_SASS_ARGUMENTS = '--precision 8 -s compressed'

# Haystack elasticsearch backend
ELASTICSEARCH_IP = get_env_variable('ELASTICSEARCH_IP')
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'search.backends.ConfigurableElasticSearchEngine',
        'URL': 'http://{0}:9200/'.format(ELASTICSEARCH_IP),
        'INDEX_NAME': 'haystack',
    },
}

# disable oscar django compressor
COMPRESS_ENABLED = False


INSTALLED_APPS += (
    'djrill',
)

# Email settings
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = get_env_variable('MANDRILL_API_KEY')
DEFAULT_FROM_EMAIL = 'smallslive@gmail.com'
DEFAULT_FROM_REGISTRATION_EMAIL = "smallsliveusers@gmail.com"

# Metrics
METRICS_SERVER_URL = "http://metrics.smallslive.com" # no trailing slash