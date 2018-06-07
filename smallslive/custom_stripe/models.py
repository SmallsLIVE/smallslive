import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from djstripe.models import INTERVALS


class StripePlanManager(models.Manager):
    def get_or_create(self, **kwargs):
        amount = kwargs.get('amount')
        interval = kwargs.get('interval')

        if not amount or not interval:
            raise ValidationError('amount and interval needed')

        nickname = '{}-{}'.format(interval, amount)

        try:
            plan = self.get(amount=amount, interval=interval)
        except self.model.DoesNotExist:
            # TODO Check if not in database but created in Stripe
            product_id = settings.STRIPE_PRODUCTS[interval]

            new_plan = stripe.Plan.create(
                amount=amount,
                interval=interval,
                nickname=nickname,
                currency='usd',
                product=product_id
            )

            plan = self.create(
                amount=amount, interval=interval, nickname=nickname,
                stripe_id=new_plan.stripe_id
            )

        return plan


class StripePlan(models.Model):
    stripe_id = models.CharField(max_length=50, unique=True)
    nickname = models.CharField(max_length=100)
    amount = models.IntegerField()
    interval = models.CharField(
        max_length=10,
        choices=INTERVALS,
        verbose_name="Interval type",
        null=False)

    objects = StripePlanManager()
