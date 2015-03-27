from django import forms
from django.contrib.auth import get_user_model

from events import forms as event_forms
from events.models import Event


User = get_user_model()

class ToggleRecordingStateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('state',)


class EventEditForm(event_forms.EventEditForm):
    def __init__(self, *args, **kwargs):
        super(EventEditForm, self).__init__(*args, **kwargs)
        del self.fields['state']


class ArtistInfoForm(forms.ModelForm):
    class Meta:
        fields = ('first_name', 'last_name')
        model = User
