import datetime
import re

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _, ungettext

import signals
import base
import utils


_recurrence_unit_days = {
    'Day': 1.,
    'Week': 7.,
    'Month': 30.4368,       # http://en.wikipedia.org/wiki/Month#Julian_and_Gregorian_calendars
    'Year': 365.2425,      # http://en.wikipedia.org/wiki/Year#Calendar_year
}

_TIME_UNIT_CHOICES = (
    ('Day', _(u'Day')),
    ('Week', _(u'Week')),
    ('Month', _(u'Month')),
    ('Year', _(u'Year')),
)


class FeatureManager(models.Manager):
    def all(self):
        return self.filter(site=Site.objects.get_current())


class Feature(models.Model):
    site = models.ManyToManyField(Site, verbose_name=_(u"site"))
    name = models.CharField(max_length=100, unique=True, null=False, verbose_name=_(u"name"))

    objects = FeatureManager()

    class Meta:
        verbose_name = _(u"feature")
        verbose_name_plural = _(u"features")

    def __unicode__(self):
        return self.name


class SubscriptionFeature(models.Model):
    feature = models.ForeignKey('subscription.Feature', verbose_name=_(u"feature"))
    subscription = models.ForeignKey('subscription.Subscription', verbose_name=_(u"subscription"))
    value = models.CharField(max_length=50, verbose_name=_(u"value"))

    class Meta:
        verbose_name = _(u"subscription feature")
        verbose_name_plural = _(u"subscription features")

    def __unicode__(self):
        return "%s - %s" % (self.feature.name, self.value)


class SubscriptionManager(models.Manager):
    def all(self):
        return self.filter(site=Site.objects.get_current())


class Subscription(models.Model):
    site = models.ManyToManyField(Site, verbose_name=_(u"site"))
    name = models.CharField(max_length=100, unique=True, null=False, verbose_name=_(u"name"))
    description = models.TextField(blank=True, verbose_name=_(u"description"))

    price = models.DecimalField(max_digits=64, decimal_places=2, verbose_name=_(u"price"))
    trial_period = models.PositiveIntegerField(null=True, blank=True, verbose_name=_(u"trial period"))
    trial_unit = models.CharField(max_length=5, null=True, blank=True,
                                  choices=((u"N", _(u"no trial")),)
                                  + _TIME_UNIT_CHOICES, verbose_name=_(u"trial unit"))
    trial_price = models.DecimalField(max_digits=64, decimal_places=2, verbose_name=_(u"trial price"))
    recurrence_period = models.PositiveIntegerField(null=True, blank=True, verbose_name=_(u"recurrence period"))
    recurrence_unit = models.CharField(max_length=5, null=True,
                                       choices=((u"N", _(u"no recurrence")),)
                                       + _TIME_UNIT_CHOICES, verbose_name=_(u"recurrence unit"))
    group = models.ForeignKey(Group, null=False, blank=False, verbose_name=_(u"group"))
    best_choice = models.BooleanField(default=False, verbose_name=_(u"best choice"))

    objects = SubscriptionManager()

    _PLURAL_UNITS = {
        'Day': 'days',
        'Week': 'weeks',
        'Month': 'months',
        'Year': 'years',
    }

    class Meta:
        ordering = ('price', '-recurrence_period')
        verbose_name = _(u"subscription")
        verbose_name_plural = _(u"subscriptions")

    def __unicode__(self):
        return self.name

    def price_per_day(self):
        """Return estimate subscription price per day, as a float.

        This is used to charge difference when user changes
        subscription.  Price returned is an estimate; month length
        used is 30.4368 days, year length is 365.2425 days (averages
        including leap years).  One-time payments return 0.
        """
        if self.recurrence_unit is None:
            return 0
        return float(self.price) / (
            self.recurrence_period * _recurrence_unit_days[self.recurrence_unit]
        )

    @models.permalink
    def get_absolute_url(self):
        return ('subscription_detail', (), dict(object_id=str(self.id)))

    def get_pricing_display(self):
        if self.price == 0:
            return _(u'free')
        elif self.recurrence_period:
            return ungettext('%(price).02f / %(unit)s',
                             '%(price).02f / %(period)d %(unit_plural)s',
                             self.recurrence_period) % {
                                 'price': self.price,
                                 'unit': self.get_recurrence_unit_display(),
                                 'unit_plural': _(self._PLURAL_UNITS[self.recurrence_unit],),
                                 'period': self.recurrence_period,
                             }
        else:
            return _('%(price).02f one-time fee') % {'price': self.price}

    @property
    def simple_display(self):
        return self.get_simple_display()

    def get_simple_display(self):
        if self.price == 0:
            return _(u'free')
        elif self.recurrence_period:
            return _(u'per %s') % self.get_recurrence_unit_display()

        else:
            return _(u'one-time fee')

    def get_trial_display(self):
        if self.trial_period:
            return ungettext('%(unit)s',
                             '%(period)d %(unit_plural)s',
                             self.trial_period) % {
                                 'unit': self.get_trial_unit_display().lower(),
                                 'unit_plural': _(self._PLURAL_UNITS[self.trial_unit],),
                                 'period': self.trial_period,
                             }
        else:
            return _(u"no trial")


def __user_get_subscription(user):
    if not hasattr(user, '_subscription_cache'):
        sl = UserSubscription.objects.get(user=user, active=True)
        if sl:
            user._subscription_cache = sl
        else:
            user._subscription_cache = None
    return user._subscription_cache
User.add_to_class('get_subscription', __user_get_subscription)


class UserSubscriptionManager(models.Manager):
    def get_active(self):
        return self.filter(active=True)

    def get_site(self):
        return self.filter(subscription__site=Site.objects.get_current())


class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(u"user"))
    subscription = models.ForeignKey(Subscription, verbose_name=_(u"subscription"))
    start = models.DateField(auto_now=True, verbose_name=_(u"start"))
    expires = models.DateField(null=True, default=datetime.date.today, verbose_name=_(u"expires"))
    active = models.BooleanField(default=True, verbose_name=_(u"active"))
    cancelled = models.BooleanField(default=True, verbose_name=_(u"cancelled"))

    grace_timedelta = datetime.timedelta(
        getattr(settings, 'SUBSCRIPTION_GRACE_PERIOD', 2))

    objects = UserSubscriptionManager()

    class Meta:
        unique_together = (('user', 'subscription'), )
        verbose_name = _(u"user subscription")
        verbose_name_plural = _(u"user subscriptions")

    def get_features(self):
        return self.subscription.subscriptionfeature_set.all()

    def user_is_group_member(self):
        "Returns True is user is member of subscription's group"
        return self.subscription.group in self.user.groups.all()
    user_is_group_member.boolean = True

    def expired(self):
        """Returns true if there is more than SUBSCRIPTION_GRACE_PERIOD
        days after expiration date."""
        return self.expires is not None and (
            self.expires + self.grace_timedelta < datetime.date.today())
    expired.boolean = True

    def valid(self):
        """Validate group membership.

        Returns True if not expired and user is in group, or expired
        and user is not in group."""
        if self.expired() or not self.active:
            return not self.user_is_group_member()
        else:
            return self.user_is_group_member()
    valid.boolean = True

    def unsubscribe(self):
        """Unsubscribe user."""
        self.user.groups.remove(self.subscription.group)
        self.active = False
        self.user.save()
        self.save()

    def subscribe(self):
        """Subscribe user."""
        self.user.groups.add(self.subscription.group)
        self.active = True
        self.start = datetime.date.today
        self.user.save()
        self.save()

    def fix(self):
        """Fix group membership if not valid()."""
        if not self.valid():
            if self.expired() or not self.active:
                self.unsubscribe()
                if self.cancelled:
                    self.delete()
            else:
                self.subscribe()

    def extend(self, timedelta=None):
        """Extend subscription by `timedelta' or by subscription's
        recurrence period."""
        if timedelta is not None:
            self.expires += timedelta
        else:
            if self.subscription.recurrence_unit:
                self.expires = utils.extend_date_by(
                    self.expires,
                    self.subscription.recurrence_period,
                    self.subscription.recurrence_unit)
            else:
                self.expires = None

    def try_change(self, subscription):
        """Check whether upgrading/downgrading to `subscription' is possible.

        If subscription change is possible, returns false value; if
        change is impossible, returns a list of reasons to display.

        Checks are performed by sending
        subscription.signals.change_check with sender being
        UserSubscription object, and additional parameter
        `subscription' being new Subscription instance.  Signal
        listeners should return None if change is possible, or a
        reason to display.
        """
        if self.subscription == subscription:
            if self.active and self.cancelled:
                return None  # allow resubscribing
            return [_(u'This is your current subscription.')]
        return [
            res[1]
            for res in signals.change_check.send(
                self, subscription=subscription)
            if res[1]]

    @models.permalink
    def get_absolute_url(self):
        return ('subscription_usersubscription_detail',
               (), dict(object_id=str(self.id)))

    def __unicode__(self):
        rv = u"%s's %s" % (self.user, self.subscription)
        if self.expired():
            rv += u' (expired)'
        return rv

#This should work once per day with a cronjob


def unsubscribe_expired():
    """Unsubscribes all users whose subscription has expired.

    Loops through all UserSubscription objects with `expires' field
    earlier than datetime.date.today() and forces correct group
    membership."""
    for us in UserSubscription.objects.filter(expires__lt=datetime.date.today()):
        us.fix()


class ExpressTransaction(base.ResponseModel):
    # The PayPal method and version used
    method = models.CharField(max_length=32, verbose_name=_(u"method"))
    version = models.CharField(max_length=8, verbose_name=_(u"version"))

    # Transaction details used in GetExpressCheckout
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True,
                                 blank=True, verbose_name=_(u"amount"))
    currency = models.CharField(max_length=8, null=True, blank=True, verbose_name=_(u"currency"))

    # Response params
    SUCCESS, SUCCESS_WITH_WARNING, FAILURE = 'Success', 'SuccessWithWarning', 'Failure'
    ack = models.CharField(max_length=32, verbose_name=_(u"ack"))

    correlation_id = models.CharField(max_length=32, null=True, blank=True, verbose_name=_(u"correlation id"))
    token = models.CharField(max_length=32, null=True, blank=True, verbose_name=_(u"token"))

    profile_id = models.CharField(max_length=32, verbose_name=_(u"profile id"))
    profile_status = models.CharField(max_length=32, verbose_name=_(u"profile status"))

    error_code = models.CharField(max_length=32, null=True, blank=True, verbose_name=_(u"error code"))
    error_message = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(u"error message"))

    class Meta:
        ordering = ('-date_created',)
        verbose_name = _(u"express transaction")
        verbose_name_plural = _(u"express transactions")

    def save(self, *args, **kwargs):
        self.raw_request = re.sub(r'PWD=\d+&', 'PWD=XXXXXX&', self.raw_request)
        return super(ExpressTransaction, self).save(*args, **kwargs)

    @property
    def is_successful(self):
        return self.ack in (self.SUCCESS, self.SUCCESS_WITH_WARNING)

    def __unicode__(self):
        return u'method: %s: token: %s' % (
            self.method, self.token)
