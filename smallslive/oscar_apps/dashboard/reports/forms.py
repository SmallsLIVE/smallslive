from django import forms
from django.utils.translation import gettext_lazy as _
from oscar.apps.dashboard.reports import forms as oscar_forms
from oscar.forms.widgets import DatePickerInput
from events.models import Venue


class ReportForm(oscar_forms.ReportForm):
    date_from = forms.DateField(label=_("Date from"), required=False,
                                widget=DatePickerInput)
    date_to = forms.DateField(label=_("Date to"),
                              help_text=_("The report is inclusive of this"
                                          " date"),
                              required=False,
                              widget=DatePickerInput)


class TicketReportForm(ReportForm):
    venue = forms.ModelChoiceField(label=_("Venue"),
                                   queryset=Venue.objects.order_by('name'),
                                   empty_label=_("All venues"),
                                   required=False)

    field_order = ['report_type', 'venue', 'date_from', 'date_to', 'download']