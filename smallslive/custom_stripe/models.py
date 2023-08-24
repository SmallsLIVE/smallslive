import stripe
from djstripe.models import Customer, Plan
from django.db import models


class CustomPlan(models.Model):
    """Cannot upgrade dj-stripe until Django upgrades to 1.11
    This class overrides the Plan class in order to inject
    the 'product' parameter.
    """

    @classmethod
    def create(cls, metadata={}, **kwargs):
        """Create and then return a Plan (both in Stripe, and in our db)."""

        print('CustomPlan:create ->')
        print(kwargs)

        plan = stripe.Plan.create(
            amount=int(kwargs['amount'] * 100),
            currency=kwargs['currency'],
            interval=kwargs['interval'],
            interval_count=kwargs.get('interval_count', None),
            product=kwargs.get('product'),
            trial_period_days=kwargs.get('trial_period_days'),
            metadata=metadata)

        plan = Plan.objects.create(
            id=plan.id,
            active= True,
            amount=kwargs['amount'],
            currency=kwargs['currency'],
            interval=kwargs['interval'],
            interval_count=kwargs.get('interval_count', None),
            nickname='Archive Access',
            trial_period_days=kwargs.get('trial_period_days'),
        )

        return plan


class CustomerDetail(models.Model):
    """Store billing information on Stripe
     This version of djstripe does not support this
     """

    @classmethod
    def get(cls, **kwargs):
        try:
            customer = stripe.Customer.retrieve(kwargs.get('id'))
        except:
            customer = None

        return customer
