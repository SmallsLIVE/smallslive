from .local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'TEST': {'NAME': 'db.sqlite3'},
    }
}

ACCOUNT_EMAIL_VERIFICATION = 'optional'
# not needed for tests
STRIPE_PUBLISHABLE_KEY = ''
STRIPE_SECRET_KEY = ''

MIGRATION_MODULES = {'address': 'address.notmigrations',
                     'admin': 'admin.notmigrations',
                     'analytics': 'analytics.notmigrations',
                     'artists': 'artists.notmigrations',
                     'auth': 'auth.notmigrations',
                     'basket': 'basket.notmigrations',
                     'catalogue': 'catalogue.notmigrations',
                     'contenttypes': 'contenttypes.notmigrations',
                     'customer': 'customer.notmigrations',
                     'django_extensions': 'django_extensions.notmigrations',
                     'events': 'events.notmigrations',
                     'facebook': 'facebook.notmigrations',
                     'flatpages': 'flatpages.notmigrations',
                     'multimedia': 'multimedia.notmigrations',
                     'offer': 'offer.notmigrations',
                     'order': 'order.notmigrations',
                     'partner': 'partner.notmigrations',
                     'payment': 'payment.notmigrations',
                     'promotions': 'promotions.notmigrations',
                     'reviews': 'reviews.notmigrations',
                     'sessions': 'sessions.notmigrations',
                     'shipping': 'shipping.notmigrations',
                     'sites': 'sites.notmigrations',
                     'socialaccount': 'socialaccount.notmigrations',
                     'twitter': 'twitter.notmigrations',
                     'users': 'users.notmigrations',
                     'voucher': 'voucher.notmigrations',
                     # Only for upgrade purpose @TODO : Fix later
                    # 'wishlists': 'wishlists.notmigrations'

                     }
