from django import forms
from filer.models.filemodels import File, Folder


class FileForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'file')
        model = File

    def __init__(self, *args, **kwargs):
        self.folder_name = kwargs.pop("folder_name", "Temp")
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['file'].required = True

    def save(self, commit=True):
        object = super(FileForm, self).save(commit=False)
        folder, created = Folder.objects.get_or_create(name=self.folder_name)
        object.folder = folder
        object.save()
        return object
