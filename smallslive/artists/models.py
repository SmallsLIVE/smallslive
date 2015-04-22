from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum, Count
from django.utils.functional import cached_property
from django.utils.text import slugify
from allauth.account.models import EmailAddress, EmailConfirmation
from image_cropping import ImageRatioField
from model_utils import Choices
from sortedm2m.fields import SortedManyToManyField
from tinymce import models as tinymce_models
from events.models import Event, GigPlayed
from users.models import SmallsEmailAddress, SmallsUser


class Artist(models.Model):
    SALUTATIONS = Choices('Mr.', 'Mrs.', 'Ms.')

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    salutation = models.CharField(choices=SALUTATIONS, max_length=255, blank=True)
    instruments = SortedManyToManyField('Instrument', blank=True, related_name='artists')
    biography = tinymce_models.HTMLField(blank=True)
    website = models.URLField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='artist_images', max_length=150, blank=True)
    cropping = ImageRatioField('photo', '580x400', help_text="Enable cropping", allow_fullsize=True)
    slug = models.SlugField(blank=True, max_length=100)

    class Meta:
        ordering = ['last_name']

    def __unicode__(self):
        return u"{0} {1}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def full_name(self):
        return u"{0} {1}".format(self.first_name, self.last_name)

    def upcoming_events(self):
        return Event.objects.upcoming().filter(performers=self)

    def past_events(self):
        return Event.objects.past().filter(performers=self)

    def get_instruments(self):
        return "\n".join([i.name for i in self.instruments.all()])

    def get_main_instrument_name(self):
        instrument = self.instruments.first()
        if instrument:
            return instrument.name
        else:
            return ""

    def events_count(self):
        return self.events.count()

    def media_count(self):
        return self.events.annotate(cnt=Count('sets')).aggregate(count=Sum('cnt'))['count']

    def media_count_as_leader(self):
        return self.gigs_played.filter(is_leader=True).annotate(
            cnt=Count('event__sets')).aggregate(count=Sum('cnt'))['count']

    def media_count_as_sideman(self):
        return self.gigs_played.filter(is_leader=False).annotate(
            cnt=Count('event__sets')).aggregate(count=Sum('cnt'))['count']

    def send_invitation(self, request, email, invite_text=None):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email, is_active=False)
        self.user = user
        self.save()
        email_model, created = SmallsEmailAddress.objects.get_or_create(user=user, email=email)
        email_model.send_confirmation(request, signup=True, invite_text=invite_text)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.full_name())
        super(Artist, self).save(force_insert, force_update, using, update_fields)

    def autocomplete_label(self):
        return self.full_name()

    def autocomplete_sublabel(self):
        return self.get_main_instrument_name()

    def is_leader_for_event(self, event):
        return GigPlayed.objects.filter(artist=self, event=event, is_leader=True).exists()

    @cached_property
    def is_invited(self):
        if hasattr(self, 'user'):
            user = self.user
            return EmailAddress.objects.filter(email=user.email).exists()
        else:
            return False

    @cached_property
    def has_registered(self):
        if hasattr(self, 'user'):
            user = self.user
            return EmailAddress.objects.filter(email=user.email, verified=True).exists()
        else:
            return False

    @cached_property
    def has_signed_legal(self):
        if hasattr(self, 'user'):
            return self.user.legal_agreement_acceptance
        else:
            return False

    @cached_property
    def email_invitation(self):
        if hasattr(self, 'user'):
            return EmailConfirmation.objects.filter(email_address__email=self.user.email).order_by('-sent').first()
        else:
            return False

    @cached_property
    def photo_crop_box(self):
        if not self.cropping or '-' in self.cropping:
            return
        top_x, top_y, bottom_x, bottom_y = self.cropping.split(',')
        return ((top_x, top_y), (bottom_x, bottom_y))


class Instrument(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "{0}?instrument={1}".format(reverse("artist_search"), self.id)

    def autocomplete_label(self):
        return self.name

    def autocomplete_sublabel(self):
        return u""
