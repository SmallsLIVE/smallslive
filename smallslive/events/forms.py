from oscar.core.loading import get_class
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Field, LayoutObject, TEMPLATE_PACK
from django import forms
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
from extra_views import InlineFormSet
import floppyforms
from haystack.forms import SearchForm

from .models import EventSet, Event, GigPlayed, Comment

from utils.widgets import ImageCropWidget


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


class GigPlayedAddInlineFormSet(InlineFormSet):
    model = GigPlayed
    fields = ('artist', 'role', 'is_leader', 'is_admin', 'sort_order')
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
            form.fields['is_leader'].initial = False
            form.fields['is_leader'].label = 'Leader'
            form.fields['is_admin'].label = 'Admin'
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


class EventSetInlineFormset(InlineFormSet):
    model = EventSet
    fields = ('start', 'end')
    extra = 1

    def construct_formset(self):
        if self.object and self.object.sets.count() > 0:
            self.extra = 0
        formset = super(EventSetInlineFormset, self).construct_formset()
        for num, form in enumerate(formset):
            form.fields['DELETE'].widget = forms.HiddenInput()
            form.fields['start'].widget = forms.TimeInput(format='%I:%M %p')
            form.fields['start'].input_formats = ['%I:%M %p']
            form.fields['end'].widget = forms.TimeInput(format='%I:%M %p')
            form.fields['end'].input_formats = ['%I:%M %p']

        return formset


class EventSetInlineFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(EventSetInlineFormsetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.field_template = 'bootstrap3/layout/inline_field.html'
        self.template = 'form_widgets/table_inline_formset.html'
        self.form_show_labels = False
        self.sortable = False


class EventAddForm(forms.ModelForm):
    start = forms.DateTimeField(label="Start time", required=True, input_formats=settings.DATETIME_INPUT_FORMATS)
    end = forms.DateTimeField(label="End time", required=True, input_formats=settings.DATETIME_INPUT_FORMATS)
    date = forms.DateField(label="Event Date", required=True)
    staff_pick = forms.BooleanField(label="Staff Pick", required=False)

    class Meta:
        model = Event
        fields = (
            'venue', 'date', 'start', 'end', 'id', 'title', 'subtitle', 'photo',
            'description', 'state', 'staff_pick', 'tickets_url'
        )
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

        layout = self.get_layout()

        self.helper.layout = layout
        self.fields['state'].label = "Event status"
        self.fields['photo'].label = "Flyer or Band Photo (JPG, PNG)"

        self.fields['start'].widget = forms.HiddenInput()
        self.fields['end'].widget = forms.HiddenInput()

    def get_layout(self):
        return Layout(
            'venue',
            'title',
            'subtitle',
            Field('date', css_class='datepicker'),
            Field('start', css_class='datepicker'),
            Field('end', css_class='datepicker'),
            FormActions(css_class='form-group slot-buttons'),
            Formset('sets', template='form_widgets/set_formset_layout.html'),
            Formset('artists', template='form_widgets/formset_layout.html'),
            'photo',
            'cropping',
            'description',
            'state',
            'staff_pick',
        )


class EventEditForm(EventAddForm):
    class Meta(EventAddForm.Meta):
        fields = (
            'venue', 'title', 'subtitle', 'date', 'start', 'end',
            'start_streaming_before_minutes', 'photo', 'cropping',
            'description', 'state', 'staff_pick', 'tickets_url')


class EventSearchForm(SearchForm):
    artist = forms.IntegerField(required=False)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q') and not self.cleaned_data.get('artist'):
            return self.no_query_found()

        sqs = self.searchqueryset.filter(text__exact=self.cleaned_data['q'])

        if self.is_valid() and self.cleaned_data.get('artist'):
            sqs = sqs.filter(performers=self.cleaned_data.get('artist'))

        return sqs.load_all()

    def no_query_found(self):
        return self.searchqueryset.all()


class CommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['event_set'].widget = forms.HiddenInput()
        self.fields['content'].widget.attrs['class'] = 'form-control'
        self.fields['content'].widget.attrs[
            'placeholder'
        ] = 'Add a public comment'

    class Meta:
        model = Comment
        fields = ['content', 'event_set']


Category = get_class('catalogue.models', 'Category')
Partner = get_class('partner.models', 'Partner')
Product = get_class('catalogue.models', 'Product')
ProductCategory = get_class('catalogue.models', 'ProductCategory')
ProductClass = get_class('catalogue.models', 'ProductClass')
StockRecord = get_class('partner.models', 'StockRecord')


class TicketAddForm(forms.Form):
    form_enabled = forms.BooleanField(initial=False, required=False)
    price = forms.DecimalField(label="Ticket price ($)", required=False)
    seats = forms.IntegerField(label="Number of seats", required=False)
    set_name = forms.CharField(max_length=50, label="Set name (example: Set 1: 9-11 PM)", required=False)

    class Meta:
        fields = ('price', 'seats', 'set_name')

    def __init__(self, *args, **kwargs):
        number = kwargs.pop('number', 1)
        super(TicketAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        self.helper.layout = Layout(
            Field('form_enabled', css_class='toggle'),
            Div(
                Field('price'),
                Field('seats'),
                Field('set_name'),
                css_class='well'
            ),
        )
        self.fields['form_enabled'].label = "Add ticket to set {0}".format(number)

    def clean(self):
        cleaned_data = super(TicketAddForm, self).clean()
        form_enabled = cleaned_data.get('form_enabled', False)
        if form_enabled:
            price = cleaned_data.get('price')
            if not price:
                self._errors['price'] = self.error_class(["This field is required"])
            seats = cleaned_data.get('seats')
            if not seats:
                self._errors['seats'] = self.error_class(["This field is required"])
            set_name = cleaned_data.get('set_name')
            if not set_name:
                self._errors['set_name'] = self.error_class(["This field is required"])
        return cleaned_data

    def save(self, event):
        tickets_category, created = Category.objects.get_or_create(name="Tickets")
        product_class, created = ProductClass.objects.get_or_create(name="Tickets", requires_shipping=False)
        product = Product.objects.create(
            title=event.title,
            product_class=product_class,
            event_id=event.id,
            set=self.cleaned_data.get('set_name'),
        )
        ProductCategory.objects.create(
            product=product,
            category=tickets_category
        )
        partner, created = Partner.objects.get_or_create(name="Mezzrow")
        last_stockrecord = StockRecord.objects.order_by('-id').first()
        if last_stockrecord:
            last_id = last_stockrecord.id
        else:
            last_id = 0
        print '******** save cleaned data'
        print self.cleaned_data
        stock = StockRecord.objects.create(
            partner=partner,
            product=product,
            partner_sku=last_id + 1,
            num_in_stock=self.cleaned_data.get('seats'),
            price_excl_tax=self.cleaned_data.get('price'),
        )
        print stock
        print stock.pk
