import os
from allauth.account.models import EmailAddress, EmailConfirmation
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.urls import reverse
from django.db import models
from django.db.models import Count, Lookup, Q, Sum
from django.db.models.fields import Field
from django.utils.functional import cached_property
from django.utils.text import slugify
from image_cropping import ImageRatioField
from model_utils import Choices
from sortedm2m.fields import SortedManyToManyField
from tinymce import models as tinymce_models
from events.models import Event, GigPlayed, Recording
from multimedia.s3_storages import get_payouts_storage_object
from oscar_apps.catalogue.models import Product, ArtistProduct
from users.models import SmallsEmailAddress


def artist_image_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    path = os.path.join("artist_images/", slugify(instance.full_name()) + ext)
    return path


class InsensitiveUnaccentExact(Lookup):
    lookup_name = 'iuexact'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'UPPER(unaccent(%s)) = UPPER(unaccent(%s))' % (lhs, rhs), params

Field.register_lookup(InsensitiveUnaccentExact)


class InsensitiveUnaccentStartsWith(Lookup):
    lookup_name = 'iustartswith'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        
        return "UPPER(unaccent(%s)) LIKE UPPER(unaccent(%s || '%%%%'))" % (lhs, rhs), params

Field.register_lookup(InsensitiveUnaccentStartsWith)


class InsensitiveUnaccentContains(Lookup):
    lookup_name = 'iucontains'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        
        return "UPPER(unaccent(%s)) LIKE UPPER(unaccent('%%%%' || %s || '%%%%'))" % (lhs, rhs), params

Field.register_lookup(InsensitiveUnaccentContains)


class ArtistManager(models.Manager):

    def find_artist(self, content):

        first_name = ''
        middle_or_nick_name = ''
        last_name = ''
        # First two words must be first name last name
        words = content.split(' ')
        if words:
            first_name = words.pop(0)
        if words:
            middle_or_nick_name = words.pop(0)
        if words:
            last_name = words.pop()

        artists_qs = self.filter(first_name__istartswith=first_name)
        artist_found = None
        for artist in artists_qs:
            if artist.last_name.lower() in content.lower():
                if not artist_found:
                    artist_found = artist
                else:
                    # artist has a possible match, but another was found too.
                    'Print: parsed: ', artist_found, 'but found: ', artist, 'too.'

                print('Possible match: ', artist)
        if not artist_found:
            artists_qs = self.filter(last_name__istartswith=last_name)
            artist_found = None
            for artist in artists_qs:
                if artist.first_name.lower() in content.lower():
                    if not artist_found:
                        artist_found = artist
                    else:
                        # artist has a possible match, but another was found too.
                        'Print: parsed: ', artist_found, 'but found: ', artist, 'too.'

        if not artist_found:
            print ('Error!!!, ', content)

        return  artist_found


class Artist(models.Model):
    SALUTATIONS = Choices('Mr.', 'Mrs.', 'Ms.')

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    salutation = models.CharField(choices=SALUTATIONS, max_length=255, blank=True)
    instruments = SortedManyToManyField('Instrument', blank=True, related_name='artists')
    biography = tinymce_models.HTMLField(blank=True)
    website = models.URLField(max_length=255, blank=True)
    photo = models.ImageField(upload_to=artist_image_path, max_length=150, blank=True)
    cropping = ImageRatioField('photo', '580x580', help_text="Enable cropping", allow_fullsize=True)
    slug = models.SlugField(blank=True, max_length=100)
    current_period_seconds_played = models.BigIntegerField(default=0)
    current_period_ratio = models.DecimalField(max_digits=11, decimal_places=10, default=0)
    public_email = models.EmailField(null=True, blank=True)

    objects = ArtistManager()

    class Meta:
        ordering = ['last_name']

    def __str__(self):
        return u"{0} {1}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        search_url = reverse('search')
        url = '{}?artist_pk={}'.format(search_url, self.id)

        return url

    def full_name(self):
        return u" ".join(filter(None, [self.first_name, self.last_name]))

    def upcoming_events(self):
        return Event.objects.upcoming().filter(performers=self)

    def past_events(self):
        return Event.objects.past().filter(performers=self)

    def recently_added(self):
        return self.past_events().exclude(recordings=None)

    def get_instruments(self):
        return "\n".join([i.name for i in self.instruments.all()])

    def get_main_instrument_name(self):
        instrument = self.instruments.first()
        return instrument.name if instrument else ''

    def events_count(self):
        return self.events.count()

    def media_count(self):
        return self.events.annotate(cnt=Count('recordings')).aggregate(count=Sum('cnt'))['count']

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

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name())
        super(Artist, self).save(**kwargs)

    def autocomplete_label(self):
        return self.full_name()

    def autocomplete_sublabel(self):
        return self.get_main_instrument_name()

    def is_leader_for_event(self, event):
        return GigPlayed.objects.filter(artist=self, event=event, is_leader=True).exists()

    def recording_id_list(self):
        """
        Returns a list of all the media IDs that "belong" to the artist, meaning that the artist
        played on the event associated with the media object.
        """
        return Recording.objects.filter(event__performers=self.id).order_by('id').values_list('id', flat=True)

    def albums(self):
        return ArtistProduct.objects.filter(artist=self, product__product_class__name="Album")

    def tracks(self):
        return ArtistProduct.objects.filter(artist=self, product__product_class__name="Track")

    def has_music(self):
        return self.tracks or self.albums


    def event_id_list(self):
        """
        Returns a list of all the event IDs that the artist played on.
        """
        return self.events.order_by('id').values_list('id', flat=True)

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
        return False

    @cached_property
    def email_invitation(self):
        if hasattr(self, 'user'):
            return EmailConfirmation.objects.filter(email_address__email=self.user.email).order_by('-sent').first()
        return False

    @cached_property
    def photo_crop_box(self):
        if not self.cropping or '-' in self.cropping:
            return
        try:
            top_x, top_y, bottom_x, bottom_y = self.cropping.split(',')
            return ((int(top_x), int(top_y)), (int(bottom_x), int(bottom_y)))
        except:
            return None

    def current_period_percentage_ratio(self):
        return self.current_period_ratio * 100
    
    @property
    def archived_shows(self):
        sqs = Event.objects.filter(
            performers=self,
            recordings__media_file__isnull=False,
            recordings__state=Recording.STATUS.Published).distinct()

        return sqs.count()

    def get_photo_name_with_bucket(self):
        return f'{self.photo.storage.bucket_name}/{self.photo.name}'


class Instrument(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10, blank=True)
    artist_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{0}?instrument={1}".format(reverse("artist_search"), self.id)

    def autocomplete_label(self):
        return self.name

    def autocomplete_sublabel(self):
        return u""


class PayoutPeriodGenerationManager(models.Manager):

    def attach_admin_spreadsheet(self, start, end, output, file_name):
        instance = self.filter(period_start=start, period_end=end).first()
        if instance:
            instance.admin_payout_spreadsheet.save(file_name, ContentFile(output.read()), save=True)

    def attach_musicians_spreadsheet(self, start, end, output, file_name):
        instance = self.filter(period_start=start, period_end=end).first()
        if instance:
            instance.musicians_payout_spreadsheet.save(file_name, ContentFile(output.read()), save=True)

    def attach_donations_spreadsheet(self, start, end, output, file_name):
        instance = self.filter(period_start=start, period_end=end).first()
        if instance:
            instance.donations_spreadsheet.save(file_name, ContentFile(output.read()), save=True)


class PayoutPeriodGeneration(models.Model):
    """When calculation starts, it needs to run on a background task.
        statuses: "processing", "finished".
    """
    STATUSES = Choices('initial', 'processing', 'success', 'error')

    period_start = models.DateField()
    period_end = models.DateField()
    total_seconds = models.BigIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    admin_payout_spreadsheet = models.FileField(upload_to='payouts_generation/',
                                                storage=get_payouts_storage_object(), blank=True)
    musicians_payout_spreadsheet = models.FileField(upload_to='payouts_generation/',
                                                    storage=get_payouts_storage_object(), blank=True)
    donations_spreadsheet = models.FileField(upload_to='payouts_generation/',
                                             storage=get_payouts_storage_object(), blank=True)
    calculation_start = models.DateTimeField(auto_now_add=True)
    calculation_end = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=STATUSES, max_length=255, blank=True)
    status_message = models.TextField(blank=True, null=True)

    objects = PayoutPeriodGenerationManager()

    def __unicode__(self):
        return '{} - {} - {}'.format(self.period_start, self.period_end, self.status)


class PastPayoutPeriod(models.Model):
    period_start = models.DateField()
    period_end = models.DateField()
    total_seconds = models.BigIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    admin_payout_spreadsheet = models.FileField(upload_to='payouts/',
                                                storage=get_payouts_storage_object(), blank=True)
    musicians_payout_spreadsheet = models.FileField(upload_to='payouts/',
                                                    storage=get_payouts_storage_object(), blank=True)
    donations_spreadsheet = models.FileField(upload_to='payouts/',
                                             storage=get_payouts_storage_object(), blank=True)

    class Meta:
        ordering = ['-period_end']

    def __unicode__(self):
        return u"{0}-{1}".format(self.period_start, self.period_end)


class ArtistEarnings(models.Model):
    artist = models.ForeignKey(Artist, related_name='earnings', on_delete=models.CASCADE)
    payout_period = models.ForeignKey(PastPayoutPeriod, related_name='artist_earnings', on_delete=models.CASCADE)
    artist_seconds = models.BigIntegerField(default=0)
    artist_ratio = models.DecimalField(max_digits=11, decimal_places=10, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    ledger_balance = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    class Meta:
        ordering = ['-payout_period__period_end']

    def __unicode__(self):
        return u"{0}: ${1}".format(self.artist.full_name(), self.amount)

    def artist_percentage_ratio(self):
        return self.artist_ratio* 100


class CurrentPayoutPeriod(models.Model):
    period_start = models.DateField()
    period_end = models.DateField()
    current_total_seconds = models.BigIntegerField(default=0)

    def __unicode__(self):
        return u"{0}-{1}".format(self.period_start, self.period_end)
