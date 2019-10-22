import urllib
import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from oscar.apps.dashboard.catalogue import forms as oscar_forms
from events.models import Event, EventSet
from multimedia.models import MediaFile
from oscar_apps.partner.models import StockRecord, Partner
from oscar_apps.catalogue.models import Product, ProductClass, ArtistProduct
from artists.models import Artist


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
            product = kwargs.get('instance')

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

    def save(self, commit=True):
        event = self.cleaned_data['event']
        event_sets = EventSet.objects.filter(event=event)
        event_sets = sorted(event_sets, Event.sets_order)
        set_number = self.cleaned_data['set']
        set_number = int(set_number)
        event_set = event_sets[set_number - 1]
        product = super(ProductForm, self).save(commit=False)
        product.event_set = event_set
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


BaseTrackFormSet = inlineformset_factory(
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
        

BaseArtistFormSet = inlineformset_factory(
    Product, ArtistProduct, form=ProductArtistClassSelectForm, extra=15, max_num=25, can_order=True)


class ArtistMemberFormSet(BaseArtistFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        # This function just exists to drop the extra arguments
        super(ArtistMemberFormSet, self).__init__(*args, **kwargs)