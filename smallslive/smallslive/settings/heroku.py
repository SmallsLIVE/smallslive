import os
import urlparse
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
DATABASES['metrics'] = dj_database_url.config('METRICS_DB_URL')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
STATICFILES_STORAGE = "utils.storages.GzipManifestPipelineStorage"
PIPELINE_SASS_BINARY = 'sassc'
PIPELINE_SASS_ARGUMENTS = '--precision 8 -s compressed'

# Haystack elasticsearch backend
ELASTICSEARCH_URL = get_env_variable('SEARCHBOX_SSL_URL')
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'search.backends.ConfigurableElasticSearchEngine',
        'URL': ELASTICSEARCH_URL,
        'INDEX_NAME': 'haystack',
    },
}

# disable oscar django compressor
COMPRESS_ENABLED = False


INSTALLED_APPS += (
    'djrill',
    'raven.contrib.django.raven_compat',
)

# Sentry
RAVEN_CONFIG = {
    'dsn': get_env_variable('SENTRY_DSN'),
}

# Email settings
# EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
# MANDRILL_API_KEY = get_env_variable('MANDRILL_API_KEY')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.mandrilapp.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "smallslive@appsembler.com"
EMAIL_HOST_PASSWORD = get_env_variable('MANDRILL_API_KEY')
DEFAULT_FROM_EMAIL = 'smallslive@gmail.com'
DEFAULT_FROM_REGISTRATION_EMAIL = "smallsliveusers@gmail.com"
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''

# Metrics
METRICS_SERVER_URL = "https://ssltestmetrics.smallslive.com"  # no trailing slash

# Cache
redis_url = urlparse.urlparse(get_env_variable('REDIS_URL'))
CACHEOPS_REDIS = {
    'host': redis_url.hostname ,
    'port': redis_url.port,
    'db': 1,
    'password': redis_url.password,
    'socket_timeout': 5,   # connection timeout in seconds, optional
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

    'artists.*': {'ops': 'all', 'timeout': 5*60},
    'events.*': {'ops': 'all', 'timeout': 5*60},
    'multimedia.*': {'ops': 'all', 'timeout': 5*60},

    'catalogue.*': {'ops': 'all', 'timeout': 5*60},

    # And since ops is empty by default you can rewrite last line as:
    '*.*': {'timeout': 60*60},
}
CACHEOPS_LRU = True
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_FAKE = True
