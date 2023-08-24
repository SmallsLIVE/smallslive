"""
Django settings for smallslive project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import ast
import os
from django.core.exceptions import ImproperlyConfigured
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
    # ('Nate Aune', 'nate@appsembler.com'),
    # ('Filip Jukic', 'filip@appsembler.com'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'foundation@smallslive.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
DEFAULT_FROM_REGISTRATION_EMAIL = DEFAULT_FROM_EMAIL

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',


    # third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'compressor',
    'crispy_forms',
    'django_extensions',
    'django_thumbor',
    'djcelery',
    'djstripe',
    'filer',
    'floppyforms',
    'image_cropping',
    'localflavor',
    'metrics',
    'wkhtmltopdf',
    #'oscar_stripe',
    'paypal',
    'pipeline',
    'rest_framework.authtoken',
    'sortedm2m',
    'storages',
    'tinymce',
    'django_tables2',
    'widget_tweaks',

    # project apps
    'artist_dashboard',
    'artist_registration',
    'artists',
    'events',
    'institutional_subscriptions',
    'multimedia',
    'newsletters',
    'old_site',
    'static_pages',
    'subscriptions',
    'users',
    'utils',
    'custom_stripe',
    'treebeard',
    ## Dependent oscar packages
    'oscar.config.Shop',
    'oscar.apps.wishlists.apps.WishlistsConfig',
    'oscar.apps.voucher.apps.VoucherConfig',
    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',
    'oscar.apps.analytics.apps.AnalyticsConfig',

    # Oscar custom apps
    'oscar_apps.config.SmallsLiveShop',
    'oscar_apps.basket.apps.BasketConfig',
    'oscar_apps.customer.apps.CustomerConfig',
    'oscar_apps.address.apps.AddressConfig',
    'oscar.apps.offer.apps.OfferConfig',
    'oscar_apps.catalogue.apps.CatalogueConfig',
    'oscar_apps.checkout.apps.CheckoutConfig',
    'oscar_apps.dashboard.apps.DashboardConfig',
    'oscar_apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar_apps.dashboard.files.apps.FilesDashboardConfig',
    'oscar_apps.dashboard.orders.apps.OrdersDashboardConfig',
    'oscar_apps.dashboard.reports.apps.ReportsDashboardConfig',
    'oscar_apps.order.apps.OrderConfig',
    'oscar_apps.partner.apps.PartnerConfig',
    'oscar_apps.payment.apps.PaymentConfig',
    # oscar_promotion is now a separate app, need to install later.
    # 'oscar_apps.promotions',
    'oscar_apps.search.apps.SearchConfig',
    'oscar_apps.shipping.apps.ShippingConfig',
] + [
    'easy_thumbnails',  # needs to go after the oscar import to avoid template tag clashes
    'sorl.thumbnail',
]

MIDDLEWARE = (
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'pipeline.middleware.MinifyHTMLMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    # 'smallslive.middleware.RedirectMiddleware',
)
TEMPLATE_DIRS = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIRS],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'oscar.apps.search.context_processors.search_form',
                # 'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
                'users.context_processors.check_account_status',
                'users.context_processors.check_if_event_confirmed_user',
                'users.context_processors.show_modal',
                'users.context_processors.clean_messages',
            ],
        },
    },
]

ROOT_URLCONF = 'smallslive.urls'

WSGI_APPLICATION = 'smallslive.wsgi.application'

AUTH_USER_MODEL = 'users.SmallsUser'

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",

    # Needed by oscar commerce
    'oscar.apps.customer.auth_backends.EmailBackend',

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
    'metrics': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive-metrics',
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

# @TODO : Check later about db_router
#DATABASE_ROUTERS = ['smallslive.db_router.MetricsRouter']


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

DATE_INPUT_FORMATS = (
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y',              # '10/25/06'
)

SHOW_TIMES = {
    # Starts with Monday
    "1": (
        ("19:30-22:00", "Early show", "7:30-10:00 PM"),
        ("22:30-1:00", "Main show", "10:30-1:00 AM"),
        ("1:00-4:00", "After hours", "1:00-4:00 AM"),
    ),
    "2": (
        ("19:30-21:00", "Early show", "7:30-9:00 PM"),
        ("21:30-0:00", "Main show", "9:30 PM-12:00 AM"),
        ("0:30-4:00", "After hours", "12:30-4:00 AM"),
    ),
    "3": (
        ("19:30-22:00", "Early bird", "7:30-10:00 PM"),
        ("22:30-1:00", "Main show", "10:30 PM-1:00 AM"),
        ("1:30-4:00", "Round midnight", "1:30-4:00 AM"),
    ),
    "4": (
        ("19:30-22:00", "Early bird", "7:30-10:00 PM"),
        ("22:30-1:00", "Main show", "10:30 PM-1:00 AM"),
        ("1:30-4:00", "Round midnight", "1:30-4:00 AM"),
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
        ("22:30-4:00", "Johnny O'Neal residency", "10:30 PM-4:00 PM"),
    )
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]
PIPELINE_STORAGE = STATICFILES_STORAGE =  'pipeline.storage.PipelineCachedStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

PIPELINE = {
    'COMPILERS': (
        'pipeline.compilers.sass.SASSCompiler',
    ),
    'JAVASCRIPT': {
        'js': {
            'source_filenames': (
                'js/jquery.mobile.custom.min.js',
                'js/jquery-ui.js',
                'js/jquery.visible.min.js',
                'js/bootstrap.min.js',
                'js/slick/slick.min.js',
                'js/raphael-min.js',
                'js/imgCoverEffect.min.js',
                'js/base.js',
                'js/utils.js',
                'js/signup_form.js',
                'js/white-border-select.js',
                'js/owl.carousel.min.js',
                'js/custom_owl_carousel.js',
                'js/custom_recently_added_carousel.js',
                'js/custom_popular_carousel.js',
                'js/custom_highlights_carousel.js',
                'js/custom_catalog_carousel.js',
            ),
            'output_filename': 'js/main.js',
        },

        'dashboard_js': {
            'source_filenames': (
                'js/jquery.mobile.custom.min.js',
                'js/jquery-ui.js',
                'js/bootstrap.min.js',
                'js/slick/slick.min.js',
                'js/raphael-min.js',
                'js/base.js',
                'js/imgCoverEffect.min.js',
                'js/bootstrap-select.js',
                'js/Chart.min.js',
                'js/dashboard-base.js'
            ),
            'output_filename': 'js/dashboard_main.js',
        }
    },

    'STYLESHEETS': {
        'css': {
            'source_filenames': (
                'sass/main.scss',
            ),
            'output_filename': 'css/application.css',
        },
        'dashboard_css': {
            'source_filenames': (
                'sass/dashboard.scss',
            ),
            'output_filename': 'css/dashboard.css',
        },
    }
}

PIPELINE_SASS_BINARY = '/usr/bin/env sass'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_SASS_ARGUMENTS = '--precision 10'
# PIPELINE_CSS = {
#     'css': {
#         'source_filenames': (
#             'sass/main.scss',
#         ),
#         'output_filename': 'css/application.css',
#     },
#     'dashboard_css': {
#         'source_filenames': (
#             'sass/dashboard.scss',
#         ),
#         'output_filename': 'css/dashboard.css',
#     },
# }
# PIPELINE_JS = {
#     'js': {
#         'source_filenames': (
#           'js/jquery.mobile.custom.min.js',
#           'js/jquery-ui.js',
#           'js/jquery.visible.min.js',
#           'js/bootstrap.min.js',
#           'js/slick/slick.min.js',
#           'js/raphael-min.js',
#           'js/imgCoverEffect.min.js',
#           'js/base.js',
#           'js/utils.js',
#           'js/signup_form.js',
#           'js/white-border-select.js',
#           'js/owl.carousel.min.js',
#           'js/custom_owl_carousel.js',
#           'js/custom_recently_added_carousel.js',
#           'js/custom_popular_carousel.js',
#           'js/custom_highlights_carousel.js',
#           'js/custom_catalog_carousel.js',
#         ),
#         'output_filename': 'js/main.js',
#     },
#     'dashboard_js': {
#         'source_filenames': (
#           'js/jquery.mobile.custom.min.js',
#           'js/jquery-ui.js',
#           'js/bootstrap.min.js',
#           'js/slick/slick.min.js',
#           'js/raphael-min.js',
#           'js/base.js',
#           'js/imgCoverEffect.min.js',
#           'js/bootstrap-select.js',
#           'js/Chart.min.js',
#           'js/dashboard-base.js'
#         ),
#         'output_filename': 'js/dashboard_main.js',
#     }
# }
PIPELINE_DISABLE_WRAPPER = True

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },

    },
    'loggers': {
        'cron': {
            'handlers': ['console',],
            'level': 'INFO'
        },
        'paypal.payflow': {
            'handlers': ['console',],
            'level': 'DEBUG'
        },
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Crispy forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Django storages / S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SECURE_URLS = True
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

# Django storages / S3 / Mezzrow
AWS_ACCESS_KEY_ID_MEZZROW = os.environ.get('AWS_ACCESS_KEY_ID_MEZZROW')
AWS_SECRET_ACCESS_KEY_MEZZROW = os.environ.get('AWS_SECRET_ACCESS_KEY_MEZZROW')
AWS_STORAGE_BUCKET_NAME_MEZZROW = os.environ.get('AWS_STORAGE_BUCKET_NAME_MEZZROW')


# Thumbor server settings
THUMBOR_MEDIA_URL = os.environ.get('THUMBOR_MEDIA_URL', "")
THUMBOR_SECURITY_KEY = os.environ.get('THUMBOR_SECURITY_KEY', "")
THUMBOR_SERVER = os.environ.get('THUMBOR_SERVER', "")
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', "")

# Allauth config
ACCOUNT_ADAPTER = 'users.adapter.SmallsLiveAdapter'
# As per Aslan's request
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_REDIRECT_URL = '/'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USER_DISPLAY = lambda u: u.display_name()
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = reverse_lazy('email_confirmed')
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = reverse_lazy('email_confirmed')
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 60
SOCIALACCOUNT_EMAIL_VERIFICATION = "mandatory"

# Mailchimp
MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = os.environ.get('MAILCHIMP_LIST_ID')  # mailing list id

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

PAYPAL_API_USERNAME = os.environ.get('PAYPAL_API_USERNAME')
PAYPAL_API_PASSWORD = os.environ.get('PAYPAL_API_PASSWORD')
PAYPAL_API_SIGNATURE = os.environ.get('PAYPAL_API_SIGNATURE')
PAYPAL_CURRENCY = 'USD'
PAYPAL_MODE = os.environ.get('PAYPAL_MODE')
PAYPAL_MEZZROW_CLIENT_ID = os.environ.get('PAYPAL_MEZZROW_CLIENT_ID')
PAYPAL_MEZZROW_CLIENT_SECRET = os.environ.get('PAYPAL_MEZZROW_CLIENT_SECRET')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
PAYPAL_FOR_PROFIT_CLIENT_ID = os.environ.get('PAYPAL_FOR_PROFIT_CLIENT_ID')
PAYPAL_FOR_PROFIT_CLIENT_SECRET = os.environ.get('PAYPAL_FOR_PROFIT_CLIENT_SECRET')

PAYPAL_PAYFLOW_VENDOR_ID = os.environ.get('PAYPAL_PAYFLOW_VENDOR_ID')
PAYPAL_PAYFLOW_USER = os.environ.get('PAYPAL_PAYFLOW_USER')
PAYPAL_PAYFLOW_PASSWORD = os.environ.get('PAYPAL_PAYFLOW_PASSWORD')
PAYPAL_PAYFLOW_PRODUCTION_MODE = ast.literal_eval(os.environ.get('PAYPAL_PAYFLOW_PRODUCTION_MODE', 'False'))
PAYPAL_PAYFLOW_DASHBOARD_FORMS = True

# Stripe account for for profit
#
STRIPE_PUBLISHABLE_KEY = STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
#STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_SECRET_KEY = 'sk_test_SrCBpROYG7Gn8gua98U0y4TK'
STRIPE_TEST_SECRET_KEY = 'sk_test_SrCBpROYG7Gn8gua98U0y4TK'
# STRIPE_TEST_SECRET_KEY = 'sk_test_GNGP0Q81aVxjEwNejnxl3xgi'
#STRIPE_PUBLIC_KEY='pk_live_GNGP0Q81aVxjEwNejnxl3xgi'
#STRIPE_PUBLIC_KEY_PROD='pk_live_GNGP0Q81aVxjEwNejnxl3xgi'
STRIPE_LIVE_MODE=False
STRIPE_CURRENCY = 'USD'
STRIPE_CHARGE_AND_CAPTURE_IN_ONE_STEP = True
STRIPE_PRODUCT = os.environ.get('STRIPE_PRODUCT')

# Stripe account for for profit
#STRIPE_FOR_PROFIT_PUBLISHABLE_KEY = STRIPE_FOR_PROFIT_PUBLIC_KEY = os.environ.get('STRIPE_FOR_PROFIT_PUBLISHABLE_KEY')
#STRIPE_FOR_PROFIT_SECRET_KEY = os.environ.get('STRIPE_FOR_PROFIT_SECRET_KEY')

DJSTRIPE_INVOICE_FROM_EMAIL = DEFAULT_FROM_EMAIL
DJSTRIPE_PRORATION_POLICY_FOR_UPGRADES = True

# Added these two lines for upgrading djstripe to 2.0.0
DJSTRIPE_WEBHOOK_VALIDATION='retrieve_event'
DJSTRIPE_FOREIGN_KEY_TO_FIELD='djstripe_id'

DJSTRIPE_PLANS = {
    # Please note that the plan names the users see are different than the
    # Stripe plans listed here. This is to ensure backwards compatibility.
    # Please find the comments in the SUBSCRIPTION_PLANS section as all of this
    # changed with the October 2016 revisions.
    "basic_yearly": {
        "stripe_plan_id": "basic_yearly",
        "name": "Basic",
        "type": 'basic',
        "description": "Audio/Video Archive & Live Video Stream Access",
        "price": 10000,  # $100.00
        "currency": "usd",
        "interval": "year"
    },
    "basic_monthly": {
        "stripe_plan_id": "basic_monthly",
        "name": "Basic",
        "type": 'basic',
        "description": "Audio/Video Archive & Live Video Stream Access",
        "price": 1000,  # $10.00
        "currency": "usd",
        "interval": "month"
    },
    "premium_yearly": {
        "stripe_plan_id": "premium_yearly",
        "name": "Premium",
        "type": 'premium',
        "description": "Benefactor Member",
        "price": 100000,  # $1000.00
        "currency": "usd",
        "interval": "year"
    },
    "premium_monthly": {
        "stripe_plan_id": "premium_monthly",
        "name": "Premium",
        "type": 'premium',
        "description": "Benefactor Member",
        "price": 10000,  # $100.00
        "currency": "usd",
        "interval": "month"
    },
    "benefactor_1": {
        "stripe_plan_id": "benefactor_1",
        "name": "Benefactor 1",
        "type": 'benefactor_1',
        "description": "Benefactor Member",
        "price": 100000,  # $1000.00
        "currency": "usd",
        "interval": "yearly"
    },
    "benefactor_2": {
        "stripe_plan_id": "benefactor_2",
        "name": "Benefactor 2",
        "type": 'benefactor_2',
        "description": "Benefactor Member",
        "price": 250000,  # $1000.00
        "currency": "usd",
        "interval": "yearly"
    },
    "benefactor_3": {
        "stripe_plan_id": "benefactor_3",
        "name": "Benefactor 3",
        "type": 'benefactor_3',
        "description": "Benefactor Member",
        "price": 500000,  # $1000.00
        "currency": "usd",
        "interval": "yearly"
    },
    "monthly": {
        "stripe_plan_id": "plan_D01xMWV5Brx2vm",
        "name": "Monthly Subscriptions",
        "type": 'monthly',
        "description": "Monthly Subscription",
        "price": 0,  # $1000.00
        "currency": "usd",
        "interval": "monthly"
    },
}

SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Live Video Stream Access',
        'id': 'free',
        'monthly': None,
        'yearly': None,
    },
    'basic': {
        # 'basic' in SUBSCRIPTION_PLANS context refers to a plan that will not
        # be selected going forward as of Oct 2016. It was left in to allow for
        # backwards compatibility.
        'name': 'Audio/Video Archive & Live Video Stream Access',
        'id': 'basic',
        'monthly': DJSTRIPE_PLANS['basic_monthly'],
        'yearly': DJSTRIPE_PLANS['basic_yearly'],
    },
    'supporter': {
        'name': 'Audio/Video Archive & Live Video Stream Access',
        'id': 'supporter',
        'monthly': DJSTRIPE_PLANS['basic_monthly'],
    },
    'premium': {
        # 'premium' in SUBSCRIPTION_PLANS context refers to a plan that will not
        # be selected going forward as of Oct 2016. It was left in to allow for
        # backwards compatibility.
        'name': 'Benefactor Member',
        'id': 'premium',
        'monthly': DJSTRIPE_PLANS['premium_monthly'],
        'yearly': DJSTRIPE_PLANS['premium_yearly'],
    },
    'benefactor_1': {
        'name': 'Benefactor Member',
        'id': 'benefactor_1',
        'yearly': DJSTRIPE_PLANS['benefactor_1'],
    },
    'benefactor_2': {
        'name': 'Benefactor Member',
        'id': 'benefactor_2',
        'yearly': DJSTRIPE_PLANS['benefactor_2'],
    },
    'benefactor_3': {
        'name': 'Benefactor Member',
        'id': 'benefactor_3',
        'yearly': DJSTRIPE_PLANS['benefactor_3'],
    },
}

OSCAR_ALLOW_ANON_CHECKOUT = True
OSCAR_DEFAULT_CURRENCY = 'USD'
OSCAR_SHOP_NAME = 'SmallsLIVE'
OSCAR_IMAGE_FOLDER = 'product_images/%Y/%m/'
OSCAR_HOMEPAGE = '/home/'
OSCAR_PRODUCTS_PER_PAGE = 12

OSCAR_DASHBOARD_NAVIGATION += [
    {
        'label': 'Files',
        'icon': 'icon-file',
        'children': [
            {
                'label': 'Press Files',
                'url_name': 'dashboard:file-list',
                'url_kwargs': {
                    "category": "press-file"
                }
            },
            {
                'label': 'Press Photos',
                'url_name': 'dashboard:file-list',
                'url_kwargs': {
                    "category": "press-photo"
                }
            },
            {
                'label': 'Photo Gallery',
                'url_name': 'dashboard:file-list',
                'url_kwargs': {
                    "category": "gallery-photo"
                }
            },
            {
                'label': 'About us photos',
                'url_name': 'dashboard:file-list',
                'url_kwargs': {
                    "category": "about-photo"
                }
            },

         ],
    },
    {
        'label': 'Tickets',
        'icon': 'icon-bar-chart',
        'url_name': 'dashboard:tickets-report-index',
    },
]

OSCAR_DASHBOARD_NAVIGATION.append(
    {
        'label': 'PayPal',
        'icon': 'icon-globe',
        'children': [
            {
                'label': 'Express transactions',
                'url_name': 'paypal-express-list',
            },
        ]
    })

OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Refunded', 'Shipped', 'Completed'),  # Completed would be for tickets
    'Completed': ('Exchanged', 'Cancelled'),
    'Cancelled': ('Refunded', ),
    'Exchanged': ('Refunded', ),
    'Shipped': (),
}
OSCAR_LINE_STATUS_PIPELINE = OSCAR_ORDER_STATUS_PIPELINE

ELASTICSEARCH_INDEX_SETTINGS = {
    'settings': {
        "number_of_shards": 1,
        "analysis": {
            "analyzer": {
                "ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "lowercase",
                    "filter": ["haystack_ngram"]
                },
                "edgengram_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "haystack_edgengram"]
                }
            },
            "tokenizer": {
                "haystack_ngram_tokenizer": {
                    "type": "nGram",
                    "min_gram": 3,
                    "max_gram": 15,
                },
                "haystack_edgengram_tokenizer": {
                    "type": "edgeNGram",
                    "min_gram": 3,
                    "max_gram": 15,
                    "side": "front"
                }
            },
            "filter": {
                "haystack_ngram": {
                    "type": "nGram",
                    "min_gram": 3,
                    "max_gram": 15
                },
                "haystack_edgengram": {
                    "type": "edgeNGram",
                    "min_gram": 1,
                    "max_gram": 15
                }
            }
        }
    }
}

ELASTICSEARCH_FIELD_MAPPINGS = {
    'edge_ngram': {'type': 'string', 'index_analyzer': 'edgengram_analyzer', 'search_analyzer': 'standard'},
    'ngram':      {'type': 'string', 'analyzer': 'ngram_analyzer'},
    'date':       {'type': 'date'},
    'datetime':   {'type': 'date'},

    'location':   {'type': 'geo_point'},
    'boolean':    {'type': 'boolean'},
    'float':      {'type': 'float'},
    'long':       {'type': 'long'},
    'integer':    {'type': 'long'},
}

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')

BITGRAVITY_SECRET = os.environ.get('BITGRAVITY_SECRET')

COUNTRIES_FIRST = [
    'US',
    'GB',
]

# Metrics
METRICS_SERVER_URL = "" # no trailing slash
PING_INTERVAL = 30

# Hijack
ENABLE_HIJACK = False
SHOW_HIJACKUSER_IN_ADMIN = False

# Celery
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
FORCE_S3_SECURE = False

WKHTMLTOPDF_CMD = '/app/bin/wkhtmltopdf'

ADMIN_EMAILS = ast.literal_eval(os.environ.get('ADMIN_EMAILS', '[]'))

# @TODO : Fix later
#REDIRECT_TO_MAINTENANCE = ast.literal_eval(os.environ.get('REDIRECT_TO_MAINTENANCE', 'False'))

AWS_PAYOUTS_BUCKET = os.environ.get('AWS_PAYOUTS_BUCKET', 'smallslivepayouts')

THUMBNAIL_DEBUG = ast.literal_eval(os.environ.get('THUMBNAIL_DEBUG', 'False'))
DEFAULT_FROM_EMAIL = OSCAR_FROM_EMAIL = 'smallslive@smallslive.com'
