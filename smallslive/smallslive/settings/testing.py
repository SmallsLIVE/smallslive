from .local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'TEST': {'NAME': 'test_db.sqlite3'},
    }
}

# not needed for tests
STRIPE_PUBLISHABLE_KEY = ''
STRIPE_SECRET_KEY = ''
