from distutils.util import strtobool

from django.db.models import Q
import django_filters

from .models import Artist, Instrument


BOOLEAN_CHOICES = (('', 'Disabled'), ('true', 'Yes'), ('false', 'No'), )


def has_photo(qs, val):
    if val == 'true':
        qs = qs.exclude(photo="")
    elif val == 'false':
        qs = qs.filter(photo="")
    return qs


def search_name(qs, val):
    if val:
        qs = qs.filter(Q(first_name__icontains=val) | Q(last_name__icontains=val))
    return qs


def has_registered(qs, val):
    if val == 'true':
        qs = qs.exclude(user__isnull=True).extra(
            where=[
                'artists_artist.id=users_smallsuser.artist_id',
                'users_smallsuser.id=account_emailaddress.user_id',
                'account_emailaddress.verified = TRUE'
            ],
            tables=['users_smallsuser', 'account_emailaddress']
        )
    elif val == 'false':
        qs = qs.exclude(user__isnull=True).extra(
            where=[
                'artists_artist.id=users_smallsuser.artist_id',
                'users_smallsuser.id=account_emailaddress.user_id',
                'account_emailaddress.verified = FALSE'
            ],
            tables=['users_smallsuser', 'account_emailaddress']
        )
    return qs


def is_invited(qs, val):
    if val == 'true':
        qs = qs.exclude(user=None)
    elif val == 'false':
        qs = qs.filter(user=None)
    return qs


def has_signed(qs, val):
    if val == 'true':
        qs = qs.exclude(user__legal_agreement_acceptance=None)
    elif val == 'false':
        qs = qs.filter(user__legal_agreement_acceptance=None)
    return qs


class ArtistFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(action=search_name)
    instruments = django_filters.ModelChoiceFilter(queryset=Instrument.objects.all())
    is_invited = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, action=is_invited)
    has_registered = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, action=has_registered)
    has_photo = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, name="photo", action=has_photo)
    signed_legal_agreement = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, action=has_signed)

    class Meta:
        fields = ['name', 'is_invited', 'has_registered', 'has_photo', 'signed_legal_agreement', 'instruments']
        model = Artist
        order_by = (
            ('last_name', 'Last name'),
            ('-last_name', 'Last name desc'),
            ('events_count', 'Events count'),
            ('-events_count', 'Events count desc'),
            ('instruments', 'Instrument'),
            ('-instruments', 'Instrument desc'),
        )
        strict = False

    def __init__(self, *args, **kwargs):
        super(ArtistFilter, self).__init__(*args, **kwargs)
        self.filters['has_registered'].label = 'Registered'
        self.filters['has_photo'].label = 'Has photo'
        self.filters['signed_legal_agreement'].label = 'Signed'

    @property
    def form(self):
        form = super(ArtistFilter, self).form  # it's a property, so there's no method call
        for field in self.Meta.fields:
            form.fields[field].widget.attrs['class'] = 'form-control selectpicker'
        form.fields['name'].widget.attrs['class'] = 'form-control search'
        form.fields['name'].widget.attrs['placeholder'] = 'Search by name'
        return form
