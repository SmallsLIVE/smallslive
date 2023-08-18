import os
from urllib.parse import urlparse
from .base import *
import dj_database_url

# SITE_ID 2 for smallslive.com/jazz/mezzrow club
SITE_ID = 2

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
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['metrics'] = dj_database_url.config('METRICS_DB_URL')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# MIDDLEWARE = ('sslify.middleware.SSLifyMiddleware',) + MIDDLEWARE
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

REDIS_URL = urlparse(get_env_variable('REDISCLOUD_URL'))

CACHEOPS_REDIS = {
    'host': REDIS_URL.hostname ,
    'port': REDIS_URL.port,
    'db': 0,
    'password': REDIS_URL.password,
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

    'artists.*': {'ops': ('fetch', 'get'), 'timeout': 5*60},
    'events.event': {'ops': ('fetch', 'get'), 'timeout': 5*60},
    # 'multimedia.*': {'ops': 'all', 'timeout': 5*60},
    #
    # 'catalogue.*': {'ops': 'all', 'timeout': 5*60},
}
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_FAKE = True

# Allow all host headers
ALLOWED_HOSTS = [
    'smallslive-staging.herokuapp.com',
    'smallslive-staging.herokuapp.com.',
    '.herokuapp.com',
    '.herokuapp.com.',
    '127.0.0.1'
]

# Static asset configuration
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
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
    'cacheops',
    'djrill',
    'raven.contrib.django.raven_compat',
)

ENABLE_HIJACK = env_var('ENABLE_HIJACK')
if ENABLE_HIJACK:
    INSTALLED_APPS += (
        'hijack',
        'compat',
    )

# Sentry
RAVEN_CONFIG = {
    'dsn': get_env_variable('SENTRY_DSN'),
}

# Static files
STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'

# Email settings
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = get_env_variable('MANDRILL_API_KEY')
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = "smtp.mandrillapp.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = "smallslive@appsembler.com"
# EMAIL_HOST_PASSWORD = get_env_variable('MANDRILL_API_KEY')
DEFAULT_FROM_EMAIL = OSCAR_FROM_EMAIL = 'smallslive-staging@smallslive.com'
DEFAULT_FROM_REGISTRATION_EMAIL = "smallslive-staging@smallslive.com"
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

# Metrics
METRICS_SERVER_URL = "https://smallslive-metrics-staging.herokuapp.com"  # no trailing slash

# Paypal
PAYPAL_SANDBOX_MODE = env_var("PAYPAL_SANDBOX_MODE", True)

# Celery
# BROKER_URL = get_env_variable("REDISCLOUD_CELERY_QUEUE_URL")
CELERY_ALWAYS_EAGER = False
CELERY_CREATE_MISSING_QUEUES = True
BROKER_POOL_LIMIT = 1
BROKER_URL = get_env_variable('CLOUDAMQP_URL')

