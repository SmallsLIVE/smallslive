from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div, Field, HTML, Button
from django import forms
from extra_views import InlineFormSet
import floppyforms
from .models import Event, GigPlayed


class EventStatusWidget(floppyforms.RadioSelect):
    template_name = 'form_widgets/event_status.html'


class SlotsTimeWidget(floppyforms.RadioSelect):
    template_name = 'form_widgets/slots_time.html'


class GigPlayedInlineFormSet(InlineFormSet):
    model = GigPlayed
    fields = ('artist', 'role', 'is_leader', 'sort_order')
    extra = 1
    can_delete = False

    def construct_formset(self):
        formset = super(GigPlayedInlineFormSet, self).construct_formset()
        for num, form in enumerate(formset):
            form.fields['sort_order'].initial = num
            form.fields['sort_order'].widget = forms.HiddenInput()
            form.fields['sort_order'].widget.attrs['class'] = "sort_order_field"
        return formset


class GigPlayedInlineFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(GigPlayedInlineFormSetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.field_template = 'bootstrap3/layout/inline_field.html'
        self.template = 'form_widgets/table_inline_formset.html'
        self.form_show_labels = False


class EventAddForm(forms.ModelForm):
    start = forms.DateTimeField(label="Start time", required=True, input_formats=['%m/%d/%Y %I:%M %p'])
    end = forms.DateTimeField(label="End time", required=True, input_formats=['%m/%d/%Y %I:%M %p'])

    class Meta:
        model = Event
        fields = ('start', 'end', 'title', 'subtitle', 'photo', 'description', 'link', 'state')
        widgets = {
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
            FormActions(
                Button('9slot', '9:00-11:00 PM', css_class='btn-success slot', data_time='21:00-23:00'),
                Button('11slot', '11:00-1:00 PM', css_class='btn-success slot', data_time='23:00-1:00'),
                Button('1slot', '1:00-3:00 AM', css_class='btn-success slot', data_time='1:00-3:00'),
                css_class='form-group'
            ),
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
