from datetime import timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div, Field
from django import forms
from django.utils.timezone import datetime
from extra_views import InlineFormSet
import floppyforms
from .models import Event, GigPlayed


class EventStatusWidget(floppyforms.RadioSelect):
    template_name = 'form_widgets/event_status.html'


class SlotsTimeWidget(floppyforms.RadioSelect):
    template_name = 'form_widgets/slots_time.html'


class GigPlayedInlineFormSet(InlineFormSet):
    model = GigPlayed
    fields = ('artist', 'role', 'is_leader')


class GigPlayedInlineFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(GigPlayedInlineFormSetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.form_class = 'form-inline'
        #self.field_template = 'bootstrap3/layout/inline_field.html'
        self.layout = Layout(
            Field('artist', css_class="selectize", placeholder="ASDBV"),
            'role',
            'is_leader'
        )


class EventAddForm(forms.ModelForm):
    start = floppyforms.SplitDateTimeField(label="Start time", required=True)
    end = floppyforms.SplitDateTimeField(label="End time", required=True)

    class Meta:
        model = Event
        fields = ('start', 'end', 'title', 'subtitle', 'photo', 'description', 'link', 'state')
        widgets = {
            #'performers': forms.SelectMultiple,
            'state': EventStatusWidget,
            'link': floppyforms.URLInput
        }

    def __init__(self, *args, **kwargs):
        super(EventAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'event_add'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('start', css_class='datepicker'),
            Field('end', css_class='datepicker'),
            'title',
            'subtitle',
            Div('photo', css_class='well'),
            'description',
            'link',
            'state',
            ButtonHolder(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )
