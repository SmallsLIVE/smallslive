import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from decimal import Decimal
from django.db import models
from django.utils import timezone
from oscar.apps.payment.models import Source
from artists.models import Artist
from events.models import Event
from oscar_apps.catalogue.models import Product
from oscar_apps.order.models import Order
from users.models import SmallsUser



class DonationManager(models.Manager):

    def total_amount_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(date__gte=start, date__lt=end, confirmed=True)

        return donations.aggregate(models.Sum('amount'))['amount__sum'] or 0.0

    def total_deductible_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(date__gte=start, date__lt=end, confirmed=True)

        return donations.aggregate(models.Sum('deductable_amount'))['deductable_amount__sum'] or 0.0

    def total_amount_foundation_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True,
            event__isnull=True, artist__isnull=True, product__isnull=True)

        return donations.aggregate(models.Sum('amount'))['amount__sum'] or 0.0
    
    def total_deductible_foundation_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True,
            event__isnull=True, artist__isnull=True, product__isnull=True)

        return donations.aggregate(models.Sum('deductable_amount'))['deductable_amount__sum'] or 0.0

    def total_amount_projects_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True, product__isnull=False).exclude(
            product__product_class__name='Gift')

        return donations.aggregate(models.Sum('amount'))['amount__sum']

    def total_deductible_projects_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True, product__isnull=False).exclude(
            product__product_class__name='Gift')

        return donations.aggregate(models.Sum('deductable_amount'))['deductable_amount__sum'] or 0.0
    
    def total_amount_shows_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True, event__isnull=False)

        return donations.aggregate(models.Sum('amount'))['amount__sum'] or 0.0

    def total_deductible_shows_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True, event__isnull=False)

        return donations.aggregate(models.Sum('deductable_amount'))['deductable_amount__sum'] or 0.0

    def total_amount_artists_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True, artist__isnull=False)

        return donations.aggregate(models.Sum('amount'))['amount__sum'] or 0.0

    def total_deductible_artists_in_range(self, start, end):
        end += relativedelta(days=1)
        donations = self.filter(
            date__gte=start, date__lt=end, confirmed=True, artist__isnull=False)

        return donations.aggregate(models.Sum('deductable_amount'))['deductable_amount__sum'] or 0.0

    def create_by_order(self, order, payment_source, artist_id=None, event_id=None, product_id=None):

        assert artist_id is None or bool(artist_id)
        assert event_id is None or bool(event_id)
        assert product_id is None or bool(product_id)

        total = order.total_incl_tax
        deductable_total = order.get_deductable_total()
        source = Source.objects.filter(order=order).first()

        donation = {
            'user': order.user,
            'order': order,
            'payment_source': payment_source,
            'currency': 'USD',
            'amount': total,
            'reference': source.reference,
            'confirmed': True,
            'deductable_amount': deductable_total,
            'product_id': product_id,
            'artist_id': artist_id,
            'event_id': event_id,
        }

        donation_obj = self.create(**donation)

        return donation_obj

    def confirm_by_reference(self, reference):

        donation = self.get(reference=reference)
        donation.confirmed = True
        donation.save()

        return donation


class Donation(models.Model):
    """One Time Donations executed
    Previously, Stripe was the only source of subscriptions.
    Now we need other model to keep track of payments.
    """

    # Initially donations would be not anonymous but now they can be
    user = models.ForeignKey(SmallsUser, related_name='donations', blank=True, null=True, on_delete=models.CASCADE)
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
    # Donations can be applied to a product, event or artist.
    artist = models.ForeignKey(Artist, blank=True, null=True,
                                related_name='donations', on_delete=models.CASCADE)

    product = models.ForeignKey(Product, blank=True, null=True,
                                related_name='donations', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, blank=True, null=True,
                              related_name='donations', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, blank=True, null=True,
                              related_name='donations', on_delete=models.CASCADE)
    sponsored_event = models.OneToOneField(Event, blank=True, null=True,
                                           related_name='sponsorship', on_delete=models.CASCADE)
    sponsored_event_dedication = models.TextField(default='')
    # We're having a $10 minimum donation instead of $100 for the whole year
    # We'll need to accrue donations as archive access in days.
    # Each donation will extend the archive access expiry date.
    # Update: Spike has requested to give access to the full year regardless amount.
    archive_access_expiry_date = models.DateField(blank=True, null=True)
    # Spike would like to be able to create donations for a specific year
    # Time is not useful. Queries will change to use this field for the tax year donations.
    donation_date = models.DateField(default=now)

    objects = DonationManager()

    def __unicode__(self):
        reference = self.reference or ''
        if self.user:
            return u'{}: {} - {} - {} - confirmed: {}'.format(self.user.email, self.amount, self.date, reference, self.confirmed)
        else:
            return u'anonymous: {} - {}'.format(self.amount, self.date)

    def get_new_expiry_date(self):

        # Currently we're debating weather give the user access to the last
        # day of the year regardless donation amount or accrue time according
        # to it.

        # Calculate expiry date: $10 / month. Remainder: $1 / 3 days.
        # Assuming amount is integer
        # Amount should be >= 10 but we're not restricting that here.
        # Should be capped to the last day of the tax year (Dec. 31st of the current year).
        try:
            amount = int(self.amount)
        except:
            amount = Decimal(self.amount)
            amount = int(amount)

        months = 0
        days = 0

        if amount > 10:
            months = amount / 10
            amount = amount % 10

        if amount:
            days = amount % 10 * 3

        # Get last donation
        last_donation = Donation.objects.filter(
            user=self.user).order_by('-donation_date').first()
        if last_donation:
            last_expiry_date = last_donation.archive_access_expiry_date
        else:
            last_expiry_date = None

        if last_expiry_date and last_expiry_date > timezone.now().date():
            new_expiry_date = last_expiry_date
        else:
            new_expiry_date = timezone.now().date()

        if months:
            new_expiry_date = new_expiry_date + relativedelta(months=months)
        if days:
            new_expiry_date = new_expiry_date + relativedelta(days=days)

        # Limit the date
        last_day = datetime.date(timezone.now().date().year, 12, 31)

        # Spike deprecated this for the time being.
        # if new_expiry_date > last_day:

        # Make the last day of the year the last day of access
        new_expiry_date = last_day

        # New request from Spike: if donation is made after Dec 1, allow access during one whole year
        today = timezone.now().date()
        if today.month == 12:
            new_expiry_date = new_expiry_date + relativedelta(months=11)

        return new_expiry_date

    def save(self, *args, **kwargs):
        # We need to create donations for other periods.
        # donation_date is now the date the donation must be accounted on.
        if not self.donation_date:
            self.donation_date = timezone.now().date()

        if not self.deductable_amount:
            self.deductable_amount = self.amount

        # Set expiry date if it's a new object.
        # Sometimes the donation can be updated to confirm=True
        # Depending on the payment flow.
        if self.pk is None:
            new_expiry_date = self.get_new_expiry_date()
            self.archive_access_expiry_date = new_expiry_date

        super(Donation, self).save(*args, **kwargs)





