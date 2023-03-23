"""
WSGI config for smallslive project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smallslive.settings")
#
# Django 1.7
# from django.core.wsgi import get_wsgi_application
# from whitenoise import WhiteNoise
#
# application = WhiteNoise(get_wsgi_application())
# application.add_files('media', prefix='media/')


# Django 2.2.28
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smallslive.settings')

application = get_wsgi_application()
