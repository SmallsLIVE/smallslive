from django.db.models import Q
import django_filters
from users.models import SmallsUser


def search_name(qs, val):
    if val:
        qs = qs.filter(Q(first_name__icontains=val) | Q(last_name__icontains=val))
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
