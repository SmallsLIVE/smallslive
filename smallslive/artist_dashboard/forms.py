from django import forms

from events.models import Event


class ToggleRecordingStateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('state',)
