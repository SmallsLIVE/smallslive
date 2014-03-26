from .base import *
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "herokudefault")

DATABASES['default'] = dj_database_url.config()
