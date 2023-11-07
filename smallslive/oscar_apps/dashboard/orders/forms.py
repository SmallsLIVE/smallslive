from django import forms
from django.utils import timezone
from oscar_apps.catalogue.models import Product
from oscar_apps.order.models import Line


class TicketModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        partner = obj.stockrecords.all().first().partner.name
        return u"{0} - {1} ({2.month}/{2.day}/{2.year})".format(partner, obj.title, obj.event_set.event.listing_date())


class TicketExchangeSelectForm(forms.Form):
    ticket = TicketModelChoiceField(
        label="Choose an event",
        empty_label=None,
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={'style': 'width:370px;'})
    )
    old_ticket_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        """
        Dynamically generate a queryset containing only future events.
        """

        old_ticket_id = kwargs.pop('old_ticket_id', None) or kwargs.get('data', {}).get('old_ticket_id')
        line = Line.objects.get(pk=old_ticket_id)
        old_set_id = line.product.event_set_id
        super(TicketExchangeSelectForm, self).__init__(*args, **kwargs)
        qs = Product.objects.select_related('event_set').filter(
            event_set__event__start__gte=timezone.localtime(timezone.now()))\
            .exclude(event_set__id=old_set_id).order_by('event_set__event__start')
        self.fields['ticket'].queryset = qs
        if old_ticket_id:
            self.fields['old_ticket_id'].initial = old_ticket_id

