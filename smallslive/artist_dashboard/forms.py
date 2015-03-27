from django import forms

from events import forms as event_forms
from events.models import Event


class ToggleRecordingStateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('state',)


class EventEditForm(event_forms.EventEditForm):
    def __init__(self, *args, **kwargs):
        super(EventEditForm, self).__init__(*args, **kwargs)
        del self.fields['state']
