from urlparse import urlparse
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div, Field, HTML, Button, LayoutObject, TEMPLATE_PACK, MultiField
from django import forms
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
from extra_views import InlineFormSet
import floppyforms
from haystack.forms import SearchForm
from model_utils import Choices
from .models import Event, GigPlayed

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib2 import urlopen
from utils.widgets import ImageCropWidget, ImageSelectWidget


class Formset(LayoutObject):
    """
    Layout object. It renders an entire formset, as though it were a Field.

    Example::

    Formset("attached_files_formset")
    """

    template = "%s/formset.html" % TEMPLATE_PACK

    def __init__(self, formset_name_in_context, template=None, **kwargs):
        self.formset_name_in_context = formset_name_in_context
        self.admin = kwargs.pop('admin', True)

        # crispy_forms/layout.py:302 requires us to have a fields property
        self.fields = []

        # Overrides class variable with an instance level variable
        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]
        return render_to_string(self.template, Context({'wrapper': self,
            'formset': formset}))



class EventStatusWidget(floppyforms.RadioSelect):
    template_name = 'form_widgets/event_status.html'


class ImageSelectField(floppyforms.ChoiceField):
    widget = ImageSelectWidget

    def __init__(self, choices=(), required=True, widget=None, label=None,
                 initial=None, help_text='', *args, **kwargs):
        queryset = self.get_queryset()
        super(ImageSelectField, self).__init__(required=required, widget=widget, label=label,
                                               initial=initial, help_text=help_text, *args, **kwargs)
        # Set the images dynamically for the imagepicker widget
        objects = list(queryset)
        if settings.AWS_S3_CUSTOM_DOMAIN:
            domain = "https://{0}".format(settings.AWS_S3_CUSTOM_DOMAIN)
        else:
            domain = settings.THUMBOR_MEDIA_URL
        objects = [(id, "{0}/{1}".format(domain, photo)) for (id, photo) in objects]
        self.choices = Choices(("", ""))
        self.choices += Choices(*objects)

    def get_queryset(self):
        return Event.objects.exclude(photo="").order_by('-id').values_list('id', 'photo')[:5]


class GigPlayedAddInlineFormSet(InlineFormSet):
    model = GigPlayed
    fields = ('artist', 'role', 'is_leader', 'sort_order')
    extra = 1
    can_delete = False

    def construct_formset(self):
        formset = super(GigPlayedAddInlineFormSet, self).construct_formset()
        for num, form in enumerate(formset):
            form.fields['artist'].empty_label = "Artist"
            form.fields['artist'].widget.attrs['class'] = "artist_field"
            form.fields['role'].empty_label = "Role"
            form.fields['role'].widget.attrs['class'] = "role_field"
            form.fields['is_leader'].initial = True
            form.fields['sort_order'].initial = num
            form.fields['sort_order'].widget = forms.HiddenInput()
            form.fields['sort_order'].widget.attrs['class'] = "sort_order_field"
        return formset


class GigPlayedEditInlineFormset(GigPlayedAddInlineFormSet):
    extra = 1
    can_delete = True

    def construct_formset(self):
        # don't automatically show extra rows if there are artists already playing
        if self.object.performers.count() > 0:
            self.extra = 0
        formset = super(GigPlayedEditInlineFormset, self).construct_formset()
        for num, form in enumerate(formset):
            form.fields['DELETE'].widget = forms.HiddenInput()
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
        fields = ('start', 'end', 'id', 'title', 'subtitle', 'photo', 'description', 'state')
        widgets = {
            'state': EventStatusWidget,
            'link': floppyforms.URLInput,
            'photo': ImageCropWidget
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
                css_class='form-group slot-buttons'
            ),
            Formset('artists', template='form_widgets/formset_layout.html'),
            'title',
            'subtitle',
            'photo',
            'cropping',
            'description',
            'state',
        )
        self.fields['state'].label = "Event status"
        self.fields['photo'].label = "Flyer or Band Photo (JPG, PNG)"


class EventEditForm(EventAddForm):
    class Meta(EventAddForm.Meta):
        fields = ('start', 'end', 'title', 'subtitle', 'photo', 'cropping', 'description', 'state')


class EventSearchForm(SearchForm):
    artist = forms.IntegerField(required=False)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        sqs = self.searchqueryset.filter(text__exact=self.cleaned_data['q'])

        if self.is_valid() and self.cleaned_data.get('artist'):
            sqs = sqs.filter(performers=self.cleaned_data.get('artist'))

        return sqs.load_all()

    def no_query_found(self):
        return self.searchqueryset.all()
