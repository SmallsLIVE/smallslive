from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from .models import Institution


class InstitutionAddForm(forms.ModelForm):
    subscription_start = forms.DateTimeField(label="Start time", required=True, input_formats=['%m/%d/%Y %I:%M %p'])
    subscription_end = forms.DateTimeField(label="End time", required=True, input_formats=['%m/%d/%Y %I:%M %p'])

    class Meta:
        model = Institution
        fields = ('name', 'subscription_start', 'subscription_end')

    def __init__(self, *args, **kwargs):
        super(InstitutionAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'institution_add'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'name',
            Field('subscription_start', css_class='datepicker'),
            Field('subscription_end', css_class='datepicker'),
            FormActions(
                css_class='form-group slot-buttons'
            ),
        )
