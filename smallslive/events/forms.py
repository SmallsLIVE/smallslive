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
    date = forms.DateField(required=True)
    time = floppyforms.ChoiceField(required=True, widget=SlotsTimeWidget, choices=Event.SETS)

    class Meta:
        model = Event
        fields = ('date', 'time', 'title', 'subtitle', 'photo', 'description', 'link', 'state')
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
            'date',
            'time',
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

    def clean(self):
        """
        Combine date and time fields to set start and end.
        """
        cleaned_data = super(EventAddForm, self).clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            start_time, end_time = time.split('-')
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()
            cleaned_data['start'] = datetime.combine(date, start_time)
            if end_time < start_time:  # if events ends on another day
                date += timedelta(days=1)
            cleaned_data['end'] = datetime.combine(date, end_time)

        return cleaned_data

    def save(self, commit=True):
        object = super(EventAddForm, self).save(commit=False)
        object.start = self.cleaned_data['start']
        object.end = self.cleaned_data['end']
        object.save()
        return object
