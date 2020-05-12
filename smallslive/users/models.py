from stripe.error import APIConnectionError, InvalidRequestError
from allauth.account import signals
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress, EmailConfirmation
from djstripe.models import Customer
from djstripe.utils import subscriber_has_active_subscription
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, Sum
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from custom_stripe.models import CustomerDetail
from model_utils import Choices
from newsletters.utils import subscribe_to_newsletter, unsubscribe_from_newsletter


class SmallsUserManager(UserManager):
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Email address must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class SmallsUser(AbstractBaseUser, PermissionsMixin):
    ACCESS_LEVELS = Choices('48-hour pass', 'Half Year Membership', 'Monthly Pass', 'Three Month Membership',
                            'admin', 'basic membership', 'benefactor_1', 'benefactor_2', 'benefactor_3',
                            'member', 'musician', 'smallslive membership', 'supporter', 'trialMember')
    PAYOUT_CHOICES = Choices('Check', 'PayPal')

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into this admin ''site.'
    )
    is_vip = models.BooleanField(
        default=False,
        help_text='Designates whether this user is a VIP and has access to audio and video'
                  ' without paying for a subscription'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.'
    )
    artist = models.OneToOneField('artists.Artist', related_name='user', blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    photo = models.ImageField(upload_to='user_photos', blank=True)
    access_level = models.CharField(choices=ACCESS_LEVELS, default='', max_length=30, blank=True)
    login_count = models.IntegerField(default=0)
    accept_agreement = models.BooleanField(default=False)
    renewal_date = models.DateField(blank=True, null=True)
    # One Time Donations will set this date to one year after the donation is made.
    archive_access_until = models.DateTimeField(blank=True, null=True)
    subscription_price = models.IntegerField(blank=True, null=True)
    company_name = models.CharField(max_length=150, blank=True)
    address_1 = models.CharField(max_length=100, blank=True)
    address_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone_1 = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=100, blank=True)
    newsletter = models.BooleanField(default=False)
    payout_method = models.CharField(max_length=10, choices=PAYOUT_CHOICES, default=PAYOUT_CHOICES.Check)
    paypal_email = models.EmailField(max_length=100, blank=True)
    taxpayer_id = models.CharField(max_length=15, blank=True)
    institution = models.ForeignKey('institutional_subscriptions.Institution',
                                    blank=True, null=True, related_name='members')

    objects = SmallsUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def display_name(self):
        """
        This is the name that's shown in the frontend - either full name if available,
        or the email address.
        """
        return self.get_full_name() or self.email

    def save(self, **kwargs):

        # Force lowercase email
        self.email = self.email.lower()

        old_email = None

        if self.pk:
            old_email = self._meta.model.objects.filter(
                id=self.id
            ).only('email').first().email

        super(SmallsUser, self).save(**kwargs)

        if old_email and old_email != self.email:
            self.update_stripe_customer(email=self.email)

    def update_stripe_customer(self, **kwargs):
        """
        :param kwargs: Update params (https://stripe.com/docs/api#customers)
        :return: bool: Wether is was updated or not.
        """
        try:
            customer = self.customer.stripe_customer
            for (key, value) in kwargs.items():
                customer[key] = value
            customer.save()
            return True
        except (Customer.DoesNotExist, InvalidRequestError):
            return False

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def full_name(self):
        # Here for site-wide consistency - model.full_name, get_full_name is here for user model requirements
        return self.get_full_name()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def get_formatted_address(self):
        """Concatenate address components"""
        address_line = self.address_1 or ''
        if self.address_2:
            address_line = '{} {}'.format(address_line, self.address_2)
        formatted_address = address_line
        if self.city:
            formatted_address = '{}, {}'.format(formatted_address, self.city)
        if self.zip:
            formatted_address = '{} {}'.format(formatted_address, self.zip)
        if self.state:
            formatted_address = '{} {}'.format(formatted_address, self.state)
        if self.country:
            formatted_address = '{}, {}'.format(formatted_address, self.country)

        return formatted_address

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    @property
    def is_artist(self):
        """
        Checks if a user has an artist model assigned
        """
        return self.artist is not None

    def subscribe_to_newsletter(self, request=None):
        if not self.newsletter:
            subscribed = subscribe_to_newsletter(self.email, request)
            if subscribed:
                self.newsletter = True
                self.save()
                return True
        return False

    def unsubscribe_from_newsletter(self, request=None):
        if self.newsletter:
            unsubscribed = unsubscribe_from_newsletter(self.email, request)
            if unsubscribed:
                self.newsletter = False
                self.save()
                return True
        return False

    def is_first_login(self):
        return self.date_joined == self.last_login

    def get_donations(self, this_year=True):
        # Assume always USD.
        qs = self.donations.filter(user=self, confirmed=True)
        if this_year:
            current_date = timezone.now()
            first_day = current_date.replace(month=1, day=1, hour=0,
                                             minute=0, second=0, microsecond=0)
            qs = qs.filter(date__gte=first_day)

        return qs

    @property
    def get_donation_amount(self, this_year=True):

        qs = self.get_donations(this_year=this_year)

        amount_data = qs.values('user_id').annotate(total_donations=Sum('amount'))
        if amount_data:
            return amount_data[0]['total_donations']
        else:
            return 0

    @property
    def get_donation_expiry_date(self):
        """ Get access expiry date """
        last_donation = self.get_donations().order_by('-date').first()
        if last_donation:
            return last_donation.archive_access_expiry_date
        else:
            return None

    def get_project_donation_amount(self, product_id):
        condition = Q(product__parent_id=product_id) | Q(product_id=product_id)
        qs = self.get_donations(this_year=False).filter(condition)
        amount_data = qs.values('user_id').annotate(total_donations=Sum('amount'))
        if amount_data:
            return amount_data[0]['total_donations']
        else:
            return 0

    @property
    def has_institutional_subscription(self):
        return self.institution is not None

    @property
    def has_active_institutional_subscription(self):
        return self.institution is not None and self.institution.is_subscription_active()

    @property
    def has_active_subscription(self):
        """Checks if a user has an active subscription."""
        return subscriber_has_active_subscription(self)

    def get_archive_access_expiry_date(self):
        """Returns date of archive access expiry for a user.
        Date is set by donations ($10 / month).
        If there is no donation yet, the user might be on a subscription.
        The new system after Jan  1st. 2020 will start accruing donations.
        """
        donation = self.donations.order_by('-date').first()
        if donation:
            return donation.archive_access_expiry_date
        else:
            try:
                subscription = self.customer.current_subscription
            except:
                return None

            return subscription.current_period_end

    @property
    def has_archive_access(self):
        """
            Monthly Pledge: existing  ($10) or new (free amount, min $10)
            Donations: min $10. $100 /year, $10/month, $1/day ** Spike  has new requested full access
            to the tax year regardless donation.
            VIPs
            Institutional Subscriptions
            Artists
        """
        today = timezone.localtime(
            timezone.now().replace(hour=0, minute=0, second=0)).date()
        date = self.get_donation_expiry_date
        return date and date >= today or \
               self.get_subscription_plan['type'] != 'free' or \
               self.is_vip or \
               self.has_active_institutional_subscription or \
               self.is_artist

    @property
    def get_subscription_plan(self):
        if self.is_staff:
            return {'name': 'Admin', 'type': 'premium'}
        elif self.is_vip:
            return {'name': 'VIP', 'type': 'premium'}
        elif self.is_artist:
            return {'name': 'Artist', 'type': 'premium'}
        elif self.has_active_institutional_subscription:
            return {'name': 'Institutional', 'type': 'premium'}
        elif self.has_institutional_subscription:
            return {'name': 'Institutional (inactive)', 'type': 'free'}
        elif self.has_active_subscription:
            plan_id = self.customer.current_subscription.plan
            if plan_id in settings.DJSTRIPE_PLANS:
                return settings.DJSTRIPE_PLANS[plan_id]
            else:
                return {
                    'name': 'Common Subscriptions',
                    'type': 'basic'
                }
        else:
            return {'name': 'Live Video Stream Access', 'type': 'free'}

    @property
    def get_current_subscription(self):
        if self.has_active_subscription:
            return self.customer.current_subscription
        else:
            return None

    @property
    def has_activated_account(self):
        has_verified_email = EmailAddress.objects.filter(user=self,
                                                         verified=True).exists()
        is_social_account = self.socialaccount_set.exists()
        return has_verified_email or is_social_account

    @property
    def can_watch_video(self):
        return self.has_activated_account and \
               self.has_archive_access

    @property
    def can_listen_to_audio(self):
        return self.has_activated_account and \
               self.has_archive_access

    def get_active_card(self):

        try:
            customer_detail = CustomerDetail.get(id=self.customer.stripe_id)
        except APIConnectionError:
            customer_detail = None
        except InvalidRequestError:
            customer_detail = None
        except CustomerDetail.DoesNotExist:
            customer_detail = None
        except SmallsUser.customer.RelatedObjectDoesNotExist:
            customer_detail = None
        if customer_detail:
            return customer_detail.active_card


class SmallsEmailConfirmation(EmailConfirmation):
    class Meta:
        proxy = True

    def send(self, request, signup=False, **kwargs):
        """
        Overridden method to enable passing kwargs to the email template.
        """
        activate_view = kwargs.pop('activate_view', 'account_confirm_email')
        current_site = kwargs["site"] if "site" in kwargs \
            else Site.objects.get_current()
        activate_url = reverse(activate_view, args=[self.key])
        activate_url = request.build_absolute_uri(activate_url)

        referer = request.META.get('HTTP_REFERER', '')

        if 'donate' in referer:
            activate_url += '?donate=True'
        elif request.GET.get('tickets'):
            activate_url += '?tickets=True'
        elif 'catalog' in referer:
            activate_url += '?catalog=True&next=' + request.GET.get('next_after_confirm', '')

        ctx = {
            'user': self.email_address.user,
            'activate_url': activate_url,
            'current_site': current_site,
            'key': self.key,
        }
        ctx.update(**kwargs)
        email_template = 'account/email/email_confirmation_signup'
        get_adapter().send_mail(email_template,
                                self.email_address.email,
                                ctx)
        self.sent = timezone.now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__,
                                             confirmation=self)


class SmallsEmailAddress(EmailAddress):
    class Meta:
        proxy = True

    def send_confirmation(self, request, signup=False, **kwargs):

        confirmation = SmallsEmailConfirmation.create(self)
        confirmation.send(request, signup=signup, **kwargs)

        return confirmation


class LegalAgreementAcceptance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='legal_agreement_acceptance')
    date = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
