"""
Django settings for smallslive project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname((__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6h%2-8&^8z0k9awraly+&t193_kc^m&l$^i_32*9%ewz_$rvu&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
#    'allauth.socialaccount.providers.linkedin',
    'allauth.socialaccount.providers.linkedin_oauth2',
#    'allauth.socialaccount.providers.openid',
#    'allauth.socialaccount.providers.persona',
#    'allauth.socialaccount.providers.soundcloud',
#    'allauth.socialaccount.providers.tumblr',
    'allauth.socialaccount.providers.twitter',
#    'allauth.socialaccount.providers.vimeo',
    'crispy_forms',
    'django_extensions',
    'django_thumbor',
    'sortedm2m',
    'south',
    'storages',
    'djstripe',
    'floppyforms',

    # project apps
    'artists',
    'events',
    'multimedia',
    'old_site',
    'users',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djstripe.middleware.SubscriptionPaymentMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
    'djstripe.context_processors.djstripe_settings',
)

ROOT_URLCONF = 'smallslive.urls'

WSGI_APPLICATION = 'smallslive.wsgi.application'

AUTH_USER_MODEL = 'users.SmallsUser'

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
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

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Templates
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'templates'),
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
#ACCOUNT_SIGNUP_FORM_CLASS = "djstripe.forms.StripeSubscriptionSignupForm"

# Stripe settings
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "<your publishable test key>")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "<your secret test key>")

DJSTRIPE_PLANS = {
    "monthly": {
        "stripe_plan_id": "basic-monthly",
        "name": "Basic Plan Monthly ($10.00/month)",
        "description": "The monthly subscription plan to SmallsLIVE",
        "price": 1000,  # $10.00
        "currency": "usd",
        "interval": "month"
    },
    "yearly": {
        "stripe_plan_id": "basic-yearly",
        "name": "Basic Plan Annual ($100/year)",
        "description": "The annual subscription plan to the Basic Plan",
        "price": 10000,  # $100.00
        "currency": "usd",
        "interval": "year"
    }
}

DJSTRIPE_INVOICE_FROM_EMAIL = ("billing@smallslive.com")

# see http://dj-stripe.readthedocs.org/en/latest/settings.html#djstripe-subscription-required-exception-urls
DJSTRIPE_SUBSCRIPTION_REQUIRED_EXCEPTION_URLS = (
    'home',
    'about',
    'static_page',
    '(events)',
    '(artists)',
    '(allauth)',  # anything in the django-allauth URLConf
)