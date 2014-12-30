"""
Django settings for smallslive project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.core.exceptions import ImproperlyConfigured
from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR
from oscar.defaults import *


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname((__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6h%2-8&^8z0k9awraly+&t193_kc^m&l$^i_32*9%ewz_$rvu&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


ADMINS = (
    ('Nate Aune', 'nate@appsembler.com'),
    ('Filip Jukic', 'filip@appsembler.com'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'smallslive@appsembler.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',


    # third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'allauth.socialaccount.providers.twitter',
    'compressor',
    'crispy_forms',
    'django_extensions',
    'django_thumbor',
    'floppyforms',
    'oscar_stripe',
    'pipeline',
    'sortedm2m',
    'storages',
    'tinymce',

    # project apps
    'artist_registration',
    'artists',
    'events',
    'multimedia',
    'old_site',
    'users',
] + get_core_apps([
    'oscar_apps.address',
    'oscar_apps.checkout',
    'oscar_apps.partner',
    'oscar_apps.shipping',
])

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
    'oscar.apps.search.context_processors.search_form',
    'oscar.apps.promotions.context_processors.promotions',
    'oscar.apps.checkout.context_processors.checkout',
    'oscar.apps.customer.notifications.context_processors.notifications',
    'oscar.core.context_processors.metadata',
)

ROOT_URLCONF = 'smallslive.urls'

WSGI_APPLICATION = 'smallslive.wsgi.application'

AUTH_USER_MODEL = 'users.SmallsUser'

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    # Needed by oscar commerce
    'oscar.apps.customer.auth_backends.EmailBackend',

    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
    },
    'old': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive_old',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', 'English'),
)

TIME_ZONE = 'America/New_York'

USE_I18N = False

USE_L10N = False

USE_TZ = True

DATETIME_INPUT_FORMATS = (
    '%m/%d/%Y %I:%M %p',     # '10/25/2006 2:30 PM'
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    '%m/%d/%y',              # '10/25/06'
)

SHOW_TIMES = {
    # Starts with Monday
    "1": (
        ("19:30-22:00", "Early show", "7:30-10:00 PM"),
        ("22:00-1:00", "Main show", "10:00-1:00 AM"),
        ("1:00-4:00", "After hours", "1:00-4:00 AM"),
    ),
    "2": (
        ("19:30-22:00", "Early show", "7:30-10:00 PM"),
        ("22:00-1:00", "Main show", "10:00-1:00 AM"),
        ("1:00-4:00", "After hours", "1:00-4:00 AM"),
    ),
    "3": (
        ("18:30-21:00", "Early bird", "6:30-9:00 PM"),
        ("21:30-0:00", "Main show", "9:30-12:00 AM"),
        ("0:30-4:00", "Round midnight", "12:30-4:00 AM"),
    ),
    "4": (
        ("18:30-21:00", "Early bird", "6:30-9:00 PM"),
        ("21:30-0:00", "Main show", "9:30-12:00 AM"),
        ("0:30-4:00", "Round midnight", "12:30-4:00 AM"),
    ),
    "5": (
        ("16:00-19:00", "Afternoon jam session", "4:00-7:00 PM"),
        ("19:30-22:00", "Early bird", "7:30-10:00 PM"),
        ("22:30-1:00", "Main show", "10:30-1:00 AM"),
        ("1:30-4:00", "Afterhours", "1:30-4:00 AM"),
    ),
    "6": (
        ("16:00-19:00", "Afternoon jam session", "4:00-7:00 PM"),
        ("19:30-22:00", "Early bird", "7:30-10:00 PM"),
        ("22:30-1:00", "Main show", "10:30-1:00 AM"),
        ("1:30-4:00", "Afterhours", "1:30-4:00 AM"),
    ),
    "7": (
        ("13:00-15:00", "Vocal workshop", "1:00-3:00 PM"),
        ("16:30-19:00", "Sunday showcase", "4:30-7:00 PM"),
        ("19:30-22:00", "Early show", "7:30-10:00 PM"),
        ("22:00-23:30", "Johnny O'Neal residency", "10:00-11:30 PM"),
        ("0:00-4:00", "Round midnight", "12:00-4:00 AM"),
    )
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PIPELINE_COMPILERS = (
    'pipeline.compilers.sass.SASSCompiler',
)
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_SASS_ARGUMENTS = '--update --precision 10'
PIPELINE_CSS = {
    'css': {
        'source_filenames': (
            'sass/application.scss',
        ),
        'output_filename': 'css/application.css',
    },
}

# Templates
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'templates'),
    OSCAR_MAIN_TEMPLATE_DIR,
]

# Messages
from django.contrib import messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger'
}

# Crispy forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Django storages / S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False

# Thumbor server settings
THUMBOR_MEDIA_URL = os.environ.get('THUMBOR_MEDIA_URL', "")
THUMBOR_SECURITY_KEY = os.environ.get('THUMBOR_SECURITY_KEY', "")
THUMBOR_SERVER = os.environ.get('THUMBOR_SERVER', "")
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', "")

# Allauth config
LOGIN_REDIRECT_URL = '/'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGOUT_ON_GET = True

# TinyMCE
TINYMCE_JS_URL = os.path.join(STATIC_URL, "js/tinymce/tinymce.min.js")
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, "js/tinymce")
TINYMCE_DEFAULT_CONFIG = {
    'theme': "modern",
    'skin': 'light',
    'toolbar': "bold italic | link",
    'menubar': False,
    'statusbar': False,
    'plugins': 'link'
}

# Oscar settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_CURRENCY = 'USD'

OSCAR_DEFAULT_CURRENCY = 'USD'
OSCAR_SHOP_NAME = 'SmallsLIVE'
OSCAR_IMAGE_FOLDER = 'product_images/%Y/%m/'
