from .local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive',
        'USER': 'nateaune',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
    'old': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'smallslive_old',
        'USER': 'nateaune',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

INSTALLED_APPS += (
    'debug_toolbar',
)

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
