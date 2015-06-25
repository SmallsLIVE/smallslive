from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from oscar.apps.dashboard.catalogue import forms as oscar_forms
from multimedia.models import MediaFile
from oscar_apps.partner.models import StockRecord, Partner
from oscar_apps.catalogue.models import Product, ProductClass


class ProductForm(oscar_forms.ProductForm):
    class Meta(oscar_forms.ProductForm.Meta):
        fields = [
            'title', 'upc', 'short_description', 'description', 'is_discountable', 'structure']


class TrackForm(forms.ModelForm):
    track_no = forms.IntegerField(required=True)
    title = forms.CharField(max_length=100, required=True)
    author = forms.CharField(max_length=100, required=True)
    track_preview_file_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    price_excl_tax = forms.DecimalField(required=False)
    track_file_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    hd_price_excl_tax = forms.DecimalField(required=False)
    hd_track_file_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

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
            self.fields['track_no'].initial = self.instance.attr.track_no
            self.fields['author'].initial = self.instance.attr.author
            try:
                file_stockrecord = self.instance.stockrecords.get(partner_sku=str(self.instance.id))
                self.fields['price_excl_tax'].initial = file_stockrecord.price_excl_tax
                self.fields['track_file_id'].initial = file_stockrecord.digital_download_id
            except StockRecord.DoesNotExist:
                pass
            try:
                file_stockrecord = self.instance.stockrecords.get(partner_sku=str(self.instance.id)+'_hd')
                self.fields['hd_price_excl_tax'].initial = file_stockrecord.price_excl_tax
                self.fields['hd_track_file_id'].initial = file_stockrecord.digital_download_id
            except StockRecord.DoesNotExist:
                pass

            if self.instance.preview:
                self.fields['track_preview_file_id'].initial = self.instance.preview_id

    def clean_track_file_id(self):
        track_file_id = self.cleaned_data['track_file_id']
        if track_file_id and not MediaFile.objects.filter(id=track_file_id).exists():
            raise ValidationError("The file must be uploaded already")
        return track_file_id

    def clean_hd_track_file_id(self):
        hd_track_file_id = self.cleaned_data['hd_track_file_id']
        if hd_track_file_id and not MediaFile.objects.filter(id=hd_track_file_id).exists():
            raise ValidationError("The file must be uploaded already")
        return hd_track_file_id

    def clean(self):
        data = super(TrackForm, self).clean()
        print data
        if data.get('track_file_id') and not data.get('price_excl_tax'):
            raise ValidationError('You need to enter the track price')

        if data.get('hd_track_file_id') and not data.get('hd_price_excl_tax'):
            raise ValidationError('You need to enter the HD track price')
        return data

    def save(self, commit=True):
        track = super(TrackForm, self).save(commit=False)
        track.attr.author = self.cleaned_data['author']
        track.attr.track_no = self.cleaned_data['track_no']
        track.ordering = self.cleaned_data['track_no']

        if self.cleaned_data['track_preview_file_id']:
            media_file = MediaFile.objects.get(id=self.cleaned_data['track_preview_file_id'])
            track.preview = media_file

        track.save()
        partner = Partner.objects.first()
        if self.cleaned_data['track_file_id']:
            stock_record, _ = StockRecord.objects.get_or_create(product=track,
                                                                partner=partner,
                                                                partner_sku=str(track.id)
                                                                )
            stock_record.price_excl_tax = self.cleaned_data['price_excl_tax']
            media_file = MediaFile.objects.get(id=self.cleaned_data['track_file_id'])
            stock_record.digital_download = media_file
            stock_record.save()

        if self.cleaned_data['hd_track_file_id']:
            stock_record, _ = StockRecord.objects.get_or_create(product=track,
                                                                partner=partner,
                                                                partner_sku=str(track.id) + "_hd"
                                                                )
            stock_record.price_excl_tax = self.cleaned_data['hd_price_excl_tax']
            media_file = MediaFile.objects.get(id=self.cleaned_data['hd_track_file_id'])
            stock_record.digital_download = media_file
            stock_record.is_hd = True
            stock_record.save()

        return track


BaseTrackFormSet = inlineformset_factory(
    Product, Product, form=TrackForm, extra=2, fk_name='album', can_order=True)


class TrackFormSet(BaseTrackFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(TrackFormSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = super(TrackFormSet, self).get_queryset()
        return qs.order_by('ordering')
