django-paypal-recurring
=======================

Django PayPal Recurring is an app for Django Framework to offer subscription using Express Checkout https://developer.paypal.com/docs/classic/express-checkout/ht_ec-recurringPaymentProfile-curl-etc/

Usage
=====

1.  'subscription' in INSTALLED_APPS
2.  Fill these settings:

    PAYPAL_API_USERNAME = 'xxxxx'
    
    PAYPAL_API_PASSWORD = 'xxxxx'
    
    PAYPAL_API_SIGNATURE = 'xxxx'
    
    PAYPAL_SANDBOX_MODE = True
    
    SITE_CURRENCY = 'EUR'

3.  in urls.py:
    
    urlpatterns = patterns('',

        ...
        url(r'^subscription/', include('subscription.urls', namespace='subscription')),
        ...
    
    )
4.  run python manage.py syncdb


Authors and Contributors
========================
bespider (@bespider) for EggForSale (@eggforsale) created Django PayPal Recurring.

Licence
=======
Django PayPal Recurring is licensed under Creative Commons Attribution-NonCommercial 3.0 license.

Licence and pricing: http://www.eggforsale.com

Support or Contact
==================
Having trouble with Django PayPal Recurring? Check out the detail page at http://www.eggforsale.com or contact support@eggforsale.com and we’ll help you sort it out.
