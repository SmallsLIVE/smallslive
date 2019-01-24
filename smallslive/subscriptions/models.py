from decimal import Decimal
from django.db import models
from users.models import SmallsUser


class Donation(models.Model):
    """One Time Donations executed
    Previously, Stripe was the only source of subscriptions.
    Now we need other model to keep track of payments.
    """
    user = models.ForeignKey(SmallsUser, related_name='donations')
    date = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=12, default='USD')
    amount = models.DecimalField(
        decimal_places=2, max_digits=12,
        default=Decimal('0.00'))

    # No need to have a payment source model for the moment.
    payment_source = models.CharField(max_length=64)
    reference = models.CharField(max_length=128, blank=True)
    # A customer-friendly label for the source, eg XXXX-XXXX-XXXX-1234
    label = models.CharField(max_length=128, blank=True)
    confirmed = models.BooleanField(default=False)





