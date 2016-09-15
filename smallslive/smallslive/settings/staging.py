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
DATABASES['default']['CONN_MAX_AGE'] = 60
#DATABASES['metrics'] = dj_database_url.config('METRICS_DB_URL')

CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_ENABLED = False

# Allow all host headers
ALLOWED_HOSTS = [
    'smallslive-staging.herokuapp.com',
    'smallslive-staging.herokuapp.com.'
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
DEFAULT_FROM_REGISTRATION_EMAIL = "smallsliveusers-staging@smallslive.com"
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

# Metrics
METRICS_SERVER_URL = "https://metrics-staging.smallslive.com"  # no trailing slash

# Paypal
PAYPAL_SANDBOX_MODE = env_var("PAYPAL_SANDBOX_MODE", True)

CELERY_ALWAYS_EAGER = True
