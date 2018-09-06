from allauth.account import signals
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress, EmailConfirmation
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from djstripe.utils import subscriber_has_active_subscription
from model_utils import Choices
from rest_framework.authtoken.models import Token
from djstripe.models import Customer
from stripe.error import InvalidRequestError

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
        :return: bool: Whether is was updated or not.
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

    @cached_property
    def has_institutional_subscription(self):
        return self.institution is not None

    @cached_property
    def has_active_institutional_subscription(self):
        return self.institution is not None and self.institution.is_subscription_active()

    @cached_property
    def has_active_subscription(self):
        """Checks if a user has an active subscription."""
        return subscriber_has_active_subscription(self)

    @cached_property
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
            return settings.DJSTRIPE_PLANS[plan_id]
        else:
            return {'name': 'Live Video Stream Access', 'type': 'free'}

    @cached_property
    def get_current_subscription(self):
        if self.has_active_subscription:
            return self.customer.current_subscription
        else:
            return None

    @cached_property
    def has_activated_account(self):
        has_verified_email = EmailAddress.objects.filter(user=self,
                                                         verified=True).exists()
        is_social_account = self.socialaccount_set.exists()
        return has_verified_email or is_social_account

    @cached_property
    def can_watch_video(self):
        return self.has_activated_account and self.get_subscription_plan['type'] != 'free'

    @cached_property
    def can_listen_to_audio(self):
        return self.has_activated_account and self.get_subscription_plan['type'] != 'free'


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
        ctx = {
            "user": self.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": self.key,
        }
        ctx.update(**kwargs)
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
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
