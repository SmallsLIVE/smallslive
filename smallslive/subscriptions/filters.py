from django.db.models import Q
import django_filters
from subscriptions.models import Donation
from users.models import SmallsUser


def search_name(qs, val):
    if val:
        qs = qs.filter(Q(first_name__icontains=val) | Q(last_name__icontains=val))
    return qs


def search_user_name(qs, val):
    if val:
        qs = qs.filter(Q(user__first_name__icontains=val) | Q(user__last_name__icontains=val))
    return qs


class SupporterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(action=search_name)

    class Meta:
        fields = ['name']
        model = SmallsUser
        order_by = (
            ('email', 'Email'),
            ('-email', 'Email desc'),
            ('last_name', 'Last name'),
            ('-last_name', 'Last name desc'),
            ('first_name', 'First name'),
            ('-first_name', 'First name desc'),
        )
        strict = False

    def __init__(self, *args, **kwargs):
        super(SupporterFilter, self).__init__(*args, **kwargs)

    @property
    def form(self):
        form = super(SupporterFilter, self).form  # it's a property, so there's no method call
        for field in self.Meta.fields:
            form.fields[field].widget.attrs['class'] = 'form-control selectpicker'
        form.fields['name'].widget.attrs['class'] = 'form-control search'
        form.fields['name'].widget.attrs['placeholder'] = 'Search by name'
        return form


class SponsorFilter(SupporterFilter):
    name = django_filters.CharFilter(action=search_user_name)
    class Meta:
        fields = ['name']
        model = Donation
        order_by = (
            ('user__email', 'Email'),
            ('-user__email', 'Email desc'),
            ('user__last_name', 'Last name'),
            ('-user__last_name', 'Last name desc'),
            ('user__first_name', 'First name'),
            ('-user__first_name', 'First name desc'),
        )
        strict = False
