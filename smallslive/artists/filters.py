from distutils.util import strtobool
from django.db.models import Q
import django_filters
from .models import Artist

BOOLEAN_CHOICES = (('', ''),('true', 'True'), ('false', 'False'), )


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


class ArtistFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(action=search_name)
    has_registered = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool,
                                                      name="user", lookup_type='isnull', exclude=True)
    has_photo = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, name="photo", action=has_photo)
    signed_legal_agreement = django_filters.TypedChoiceFilter(choices=BOOLEAN_CHOICES, coerce=strtobool,
                                                      name="user__legal_agreement_acceptance", lookup_type='isnull', exclude=True)

    class Meta:
        fields = ['name', 'has_registered', 'has_photo', 'signed_legal_agreement', 'instruments']
        model = Artist
