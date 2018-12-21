from django import forms
from django.utils import timezone
from oscar_apps.catalogue.models import Product


class TicketModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return u"{0} ({1.month}/{1.day}/{1.year})".format(obj.title, obj.event.listing_date())


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
        old_ticket_id = kwargs.pop('old_ticket_id', None)
        super(TicketExchangeSelectForm, self).__init__(*args, **kwargs)
        qs = Product.objects.select_related('event').filter(
            event__start__gte=timezone.localtime(timezone.now())).order_by('event__start')
        self.fields['ticket'].queryset = qs
        if old_ticket_id:
            self.fields['old_ticket_id'].initial = old_ticket_id
