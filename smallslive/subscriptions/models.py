from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db import models
from django.utils import timezone
from oscar_apps.catalogue.models import Product
from events.models import Event
from users.models import SmallsUser


class Donation(models.Model):
    """One Time Donations executed
    Previously, Stripe was the only source of subscriptions.
    Now we need other model to keep track of payments.
    """

    # Initially donations would be not anonymous but now they can be
    user = models.ForeignKey(SmallsUser, related_name='donations', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=12, default='USD')
    amount = models.DecimalField(
        decimal_places=2, max_digits=12,
        default=Decimal('0.00'))
    deductable_amount = models.DecimalField(
        decimal_places=2, max_digits=12,
        default=Decimal('0.00'))
    # No need to have a payment source model for the moment.
    payment_source = models.CharField(max_length=64)
    reference = models.CharField(max_length=128, blank=True)
    # A customer-friendly label for the source, eg XXXX-XXXX-XXXX-1234
    label = models.CharField(max_length=128, blank=True)
    confirmed = models.BooleanField(default=False)
    # Donations can be applied to a product
    product = models.ForeignKey(Product, blank=True, null=True,
                                related_name='donations')
    event = models.ForeignKey(Event, blank=True, null=True,
                              related_name='donations')
    # We're having a $10 minimum donation instead of $100 for the whole year
    # We'll need to accrue donations as archive access in days.
    # Each donation will extend the archive access expiry date.
    archive_access_expiry_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        if self.user:
            return u'{}: {} - {}'.format(self.user.email, self.amount, self.date)
        else:
            return u'anonymous: {} - {}'.format(self.amount, self.date)

    def get_new_expiry_date(self):
        # Calculate expiry date: $10 / month. $100 / year. Remainder: $1 / day.
        # amount >= 10

        amount = self.amount
        years = 0
        months = 0
        days = 0

        if amount >= 100:
            years = amount / 100
            amount = amount % 100

        if amount > 10:
            months = amount / 10
            amount = amount % 10

        if amount:
            days = amount % 10

        # Get last donation
        last_donation = Donation.objects.filter(
            user=self.user).order_by('-date').first()
        if last_donation:
            last_expiry_date = last_donation.archive_access_expiry_date
        else:
            last_expiry_date = None

        if last_expiry_date and last_expiry_date > timezone.now().date():
            new_expiry_date = last_expiry_date
        else:
            new_expiry_date = timezone.now().date()

        if years:
            new_expiry_date = new_expiry_date + relativedelta(years=months)
        if months:
            new_expiry_date = new_expiry_date + relativedelta(months=months)
        if days:
            new_expiry_date = new_expiry_date + relativedelta(days=days)

        return new_expiry_date

    def save(self, *args, **kwargs):
        if self.deductable_amount == 0:
            self.deductable_amount = self.amount

        # Set expiry date if it's a new object.
        # Sometimes the donation can be updated to confirm=True
        # Depending on the payment flow.
        if self.pk is None:
            new_expiry_date = self.get_new_expiry_date()
            self.archive_access_expiry_date = new_expiry_date

        super(Donation, self).save(*args, **kwargs)

    @staticmethod
    def confirm_by_reference(reference):
        donation = Donation.objects.filter(reference=reference).first()
        if donation:
            donation.confirmed = True
            donation.save()



