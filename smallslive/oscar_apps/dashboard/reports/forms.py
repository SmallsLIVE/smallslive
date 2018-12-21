from django import forms
from django.utils.translation import gettext_lazy as _
from oscar.apps.dashboard.reports import forms as oscar_forms
from oscar.forms.widgets import DatePickerInput


class ReportForm(oscar_forms.ReportForm):
    date_from = forms.DateField(label=_("Date from"), required=False,
                                widget=DatePickerInput)
    date_to = forms.DateField(label=_("Date to"),
                              help_text=_("The report is inclusive of this"
                                          " date"),
                              required=False,
                              widget=DatePickerInput)