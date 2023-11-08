from django import forms
from django.http import QueryDict
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oscar_apps.catalogue.models import Product
from oscar_apps.order.models import Line
from oscar.core.loading import get_model
from oscar.forms.widgets import DatePickerInput

SourceType = get_model('payment', 'SourceType')
Order = get_model('order', 'Order')

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


class OrderSearchForm(forms.Form):
    order_number = forms.CharField(required=False, label=_("Order number"))
    name = forms.CharField(required=False, label=_("Customer name"))
    email = forms.CharField(required=False, label=_("Customer email"))
    product_title = forms.CharField(required=False, label=_("Product name"))
    upc = forms.CharField(required=False, label=_("UPC"))
    partner_sku = forms.CharField(required=False, label=_("Partner SKU"))

    status_choices = (('', '---------'),) + tuple([(v, v)
                                                   for v
                                                   in Order.all_statuses()])
    status = forms.ChoiceField(choices=status_choices, label=_("Status"),
                               required=False)

    date_from = forms.DateField(
        required=False, label=_("Date from"), widget=DatePickerInput)
    date_to = forms.DateField(
        required=False, label=_("Date to"), widget=DatePickerInput)

    voucher = forms.CharField(required=False, label=_("Voucher code"))

    payment_method = forms.ChoiceField(
        label=_("Payment method"), required=False,
        choices=())

    format_choices = (('html', _('HTML')),
                      ('csv', _('CSV')),)
    response_format = forms.ChoiceField(widget=forms.RadioSelect,
                                        required=False, choices=format_choices,
                                        initial='html',
                                        label=_("Get results as"))

    def __init__(self, *args, **kwargs):
        # Ensure that 'response_format' is always set
        if 'data' in kwargs:
            data = kwargs['data']
            del(kwargs['data'])
        elif len(args) > 0:
            data = args[0]
            args = args[1:]
        else:
            data = None

        if data:
            if data.get('response_format', None) not in self.format_choices:
                # Handle POST/GET dictionaries, which are unmutable.
                if isinstance(data, QueryDict):
                    data = data.dict()
                data['response_format'] = 'html'

        super().__init__(data, *args, **kwargs)
        self.fields['payment_method'].choices = self.payment_method_choices()

    def payment_method_choices(self):
        return (('', '---------'),) + tuple(
            [(src.code, src.name) for src in SourceType.objects.all()])