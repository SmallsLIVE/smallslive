from dateutil import parser
import urllib
import urlparse
from oscar.apps.dashboard.catalogue import forms as oscar_forms
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from events.models import Event, EventSet
from multimedia.models import MediaFile
from oscar_apps.catalogue.models import Product, ProductClass, ArtistProduct
from oscar_apps.partner.models import StockRecord, Partner


class ProductForm(oscar_forms.ProductForm):

    class Meta(oscar_forms.ProductForm.Meta):
        fields = [
            'title',
            'subtitle',
            'upc',
            'short_description',
            'description',
            'is_discountable',
            'structure',
            'featured',
            'gift',
            'gift_price',
            'event',
            'set',
            'ordering'
        ]

    def __init__(self, product_class, data=None, parent=None, *args, **kwargs):

        self.set_initial(product_class, parent, kwargs)
        super(oscar_forms.ProductForm, self).__init__(data, *args, **kwargs)
        if product_class.slug == 'ticket':
            del self.fields['subtitle']
            del self.fields['upc']
            del self.fields['short_description']
            del self.fields['description']
            del self.fields['structure']
            del self.fields['featured']
            del self.fields['gift']
            del self.fields['gift_price']
            del self.fields['ordering']
            self.fields['event'].widget = forms.TextInput()
            self.fields['set'].widget.attrs['placeholder'] = 'Set number (i.e. 2) or set time (i.e. 7:30 pm)'
            self.fields['set_name'] = forms.CharField(required=False)
            self.fields['set_name'].widget.attrs['placeholder'] = 'Optional: special name for set'

        else:
            del self.fields['event']
            del self.fields['set']

        if parent:
            self.instance.parent = parent
            # We need to set the correct product structures explicitly to pass
            # attribute validation and child product validation. Note that
            # those changes are not persisted.
            self.instance.structure = Product.CHILD
            self.instance.parent.structure = Product.PARENT

            self.delete_non_child_fields()

            # set the child product class as it's different from the parent
            if parent.product_class.slug == "album":
                self.instance.product_class = product_class
        else:
            # Only set product class for non-child products
            self.instance.product_class = product_class
        self.add_attribute_fields(product_class, self.instance.is_parent)

        if 'title' in self.fields:
            self.fields['title'].widget = forms.TextInput(
                attrs={'autocomplete': 'off'})

        # Link event set label to a real event set object when cleaning the 'set' field.
        self.event_set = None

    def clean(self):
        """Link set number or set time with an EventSet instance"""
        cleaned_data = super(ProductForm, self).clean()

        set_number = cleaned_data.get('set')
        event = cleaned_data.get('event')

        if not event and not set_number:
            # It is not a ticket
            return

        if set_number.isdigit():
            set_number = int(set_number)
            event_sets = EventSet.objects.filter(event=event)
            event_sets = sorted(event_sets, Event.sets_order)
            try:
                self.event_set = event_sets[set_number - 1]
            except IndexError:
                raise ValidationError("Set number does not exist")
        else:
            try:
                set_time = parser.parse(set_number).time()
                self.event_set = EventSet.objects.filter(event=event, start=set_time).first()
                if not self.event_set:
                    raise ValidationError("Could not find {} for {}".format(set_time, event))
            except ValueError:
                raise ValidationError("Unrecognized set time")

    def save(self, commit=True):
        product = super(ProductForm, self).save(commit=False)

        if product.get_product_class().slug == 'ticket':
            # Linked to real object on form clean
            product.event_set = self.event_set
            # Make sure it is displayed as time. The user could have entered only the number.
            product.set = self.event_set.start.strftime('%-I:%M %p')
            # If the user provided a set name, use that instead of the set time
            set_name = self.cleaned_data['set_name']
            if set_name:
                product.set = set_name

        if commit:
            product.save()

        return product


class TrackForm(forms.ModelForm):
    track_no = forms.IntegerField(required=True)
    title = forms.CharField(max_length=100, required=True)
    composer = forms.CharField(max_length=100, required=True)
    duration = forms.CharField(max_length=5, required=False)
    #track_preview_file_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    track_preview_file = forms.CharField(max_length=300, required=False)
    price_excl_tax = forms.DecimalField(required=False)
    #track_file_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    track_file = forms.CharField(max_length=300, required=False)
    hd_price_excl_tax = forms.DecimalField(required=False)
    #hd_track_file_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    hd_track_file = forms.CharField(max_length=300, required=False)

    class Meta:
        model = Product
        fields = ('title',)
    
    def __init__(self, *args, **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        # tracks need to have a correct product class
        if not self.instance.product_class:
            self.instance.product_class = ProductClass.objects.get(slug='track')

        # show existing data correctly on the form
        if self.instance.id:
            if hasattr(self.instance.attr, 'track_no'):
                self.fields['track_no'].initial = self.instance.attr.track_no
            if hasattr(self.instance.attr, 'composer'):
                self.fields['composer'].initial = self.instance.attr.composer
            if hasattr(self.instance.attr, 'duration'):
                self.fields['duration'].initial = self.instance.attr.duration
            try:
                file_stockrecord = self.instance.stockrecords.get(partner_sku=str(self.instance.id))
                self.fields['price_excl_tax'].initial = file_stockrecord.price_excl_tax
                if file_stockrecord.digital_download:
                    self.fields['track_file'].initial = file_stockrecord.digital_download.file
            except StockRecord.DoesNotExist:
                pass
            try:
                file_stockrecord = self.instance.stockrecords.get(partner_sku=str(self.instance.id)+'_hd')
                self.fields['hd_price_excl_tax'].initial = file_stockrecord.price_excl_tax
                if file_stockrecord.digital_download:
                    self.fields['hd_track_file'].initial = file_stockrecord.digital_download.file
            except StockRecord.DoesNotExist:
                pass

            if self.instance.preview:
                self.fields['track_preview_file'].initial = self.instance.preview.file


    def clean_file(self, field_name):
        val = self.cleaned_data[field_name]
        validator = URLValidator()
        # it it's a full URL, get only the path
        try:
            validator(val)
            url = urlparse.urlparse(val)
            val = url.path
        except ValidationError:
            pass

        # don't save URL encoded values in the DB
        val = urllib.unquote(val)
        return val

    def clean_track_preview_file(self):
        return self.clean_file('track_preview_file')

    def clean_track_file(self):
        return self.clean_file('track_file')

    def clean_hd_track_file(self):
        return self.clean_file('hd_track_file')

    def clean(self):
        data = super(TrackForm, self).clean()

        preview_file = data.get('track_preview_file')
        track_file = data.get('track_file')
        hd_track_file = data.get('hd_track_file')

        if preview_file and track_file and preview_file == track_file:
            raise ValidationError("Preview and track can't be the same file")

        if preview_file and hd_track_file and preview_file == hd_track_file:
            raise ValidationError("Preview and HD track can't be the same file")

        if track_file and not data.get('price_excl_tax'):
            raise ValidationError('You need to enter the track price')

        if hd_track_file and not data.get('hd_price_excl_tax'):
            raise ValidationError('You need to enter the HD track price')
        return data

    def save(self, commit=True):
        track = super(TrackForm, self).save(commit=False)
        track.attr.composer = self.cleaned_data['composer']
        track.attr.duration = self.cleaned_data['duration']
        track.attr.track_no = self.cleaned_data['track_no']
        track.ordering = self.cleaned_data['track_no']

        if self.cleaned_data['track_preview_file']:
            try:
                preview = MediaFile.objects.get(
                    file=self.cleaned_data['track_preview_file'],
                    product=track,
                    category='preview',
                    media_type='audio',
                    format='mp3'
                )
            except MediaFile.DoesNotExist:
                preview = MediaFile.objects.create(
                    file=self.cleaned_data['track_preview_file'],
                    category='preview',
                    media_type='audio',
                    format='mp3'
                )
            track.preview = preview

        track.save()
        partner = Partner.objects.first()
        if self.cleaned_data['track_file']:
            stock_record, _ = StockRecord.objects.get_or_create(product=track,
                                                                partner=partner,
                                                                partner_sku=str(track.id)
                                                                )
            stock_record.price_excl_tax = self.cleaned_data['price_excl_tax']
            try:
                media_file = MediaFile.objects.get(
                    file=self.cleaned_data['track_file'],
                    stock_record=stock_record,
                )
            except MediaFile.DoesNotExist:
                media_file = MediaFile.objects.create(
                    file=self.cleaned_data['track_file'],
                    category='track',
                    media_type='audio',
                    format='mp3'
                )

            stock_record.digital_download = media_file
            stock_record.save()

        if self.cleaned_data['hd_track_file']:
            stock_record, _ = StockRecord.objects.get_or_create(product=track,
                                                                partner=partner,
                                                                partner_sku=str(track.id) + "_hd"
                                                                )
            stock_record.price_excl_tax = self.cleaned_data['hd_price_excl_tax']
            try:
                media_file = MediaFile.objects.get(
                    file=self.cleaned_data['hd_track_file'],
                    stock_record=stock_record,
                )
            except MediaFile.DoesNotExist:
                media_file = MediaFile.objects.create(
                    file=self.cleaned_data['hd_track_file'],
                    category='track',
                    media_type='audio',
                    format='mp3'
                )
            stock_record.digital_download = media_file
            stock_record.is_hd = True
            stock_record.save()

        return track


BaseTrackFormSet = forms.inlineformset_factory(
    Product, Product, form=TrackForm, extra=15, max_num=25, fk_name='album', can_order=True)


class TrackFormSet(BaseTrackFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(TrackFormSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = super(TrackFormSet, self).get_queryset()
        return qs.order_by('ordering')


class ProductSearchForm(forms.Form):
    upc = forms.CharField(max_length=16, required=False, label=_('UPC'))
    title = forms.CharField(
        max_length=255, required=False, label=_('Product title'))
    product_class = forms.ModelChoiceField(queryset=ProductClass.objects.all(),
                                           required=False)

    def clean(self):
        cleaned_data = super(ProductSearchForm, self).clean()
        cleaned_data['upc'] = cleaned_data['upc'].strip()
        cleaned_data['title'] = cleaned_data['title'].strip()
        return cleaned_data


class ProductArtistClassSelectForm(forms.ModelForm):

    class Meta:
        model = ArtistProduct
        fields = ('artist', 'is_leader')
        

BaseArtistFormSet = forms.inlineformset_factory(
    Product, ArtistProduct, form=ProductArtistClassSelectForm, extra=15, max_num=25, can_order=True)


class ArtistMemberFormSet(BaseArtistFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        # This function just exists to drop the extra arguments
        super(ArtistMemberFormSet, self).__init__(*args, **kwargs)