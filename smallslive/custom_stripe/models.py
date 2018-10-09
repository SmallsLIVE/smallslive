import stripe
from djstripe.models import Customer, Plan


class CustomPlan(Plan):
    """Cannot upgrade dj-stripe until Django upgrades to 1.11
    This class overrides the Plan class in order to inject
    the 'product' parameter.
    """

    @classmethod
    def create(cls, metadata={}, **kwargs):
        """Create and then return a Plan (both in Stripe, and in our db)."""

        print 'CustomPlan:create ->'
        print kwargs

        plan = stripe.Plan.create(
            amount=int(kwargs['amount'] * 100),
            currency=kwargs['currency'],
            interval=kwargs['interval'],
            interval_count=kwargs.get('interval_count', None),
            product=kwargs.get('product'),
            trial_period_days=kwargs.get('trial_period_days'),
            metadata=metadata)

        plan = Plan.objects.create(
            stripe_id=plan.stripe_id,
            amount=kwargs['amount'],
            currency=kwargs['currency'],
            interval=kwargs['interval'],
            interval_count=kwargs.get('interval_count', None),
            name='Archive Access',
            trial_period_days=kwargs.get('trial_period_days'),
        )

        return plan
