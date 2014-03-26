from .base import *

SECRET_KEY = 'codeship'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'smallslive',
    },
}
