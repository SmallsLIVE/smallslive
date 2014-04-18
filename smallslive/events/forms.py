from crispy_forms.helper import FormHelper
from django.forms import ModelForm, SelectMultiple
from .models import Event


class EventAddForm(ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'subtitle', 'description', 'start_day', 'end_day', 'link', 'photo')
        widgets = {
            'performers': SelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super(EventAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'event_add'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
