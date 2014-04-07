from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone
from model_utils import Choices


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
                          is_staff=is_staff, is_active=True,
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
                            'admin', 'basic membership', 'member', 'musician', 'smallslive membership', 'trialMember')

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into this admin ''site.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.'
    )
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

    objects = SmallsUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

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

    def is_artist(self):
        """
        Checks if a user has an artist model assigned
        """
        return self.artist != None
