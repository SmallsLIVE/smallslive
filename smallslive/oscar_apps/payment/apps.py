from oscar.apps.payment import apps


class PaymentConfig(apps.PaymentConfig):
    label = 'payment'
    name = 'oscar_apps.payment'
    verbose_name = 'Payment'
