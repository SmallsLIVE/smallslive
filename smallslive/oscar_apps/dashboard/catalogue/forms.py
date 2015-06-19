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


class TrackFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ('file',)

    def save(self, commit=True):
        file = super(TrackFileForm, self).save(commit=False)
        file.media_type = 'audio'
        file.format = 'mp3'
        file.save()
        return file


class TrackForm(forms.ModelForm):
    track_no = forms.IntegerField(required=True)
    title = forms.CharField(max_length=100, required=True)
    author = forms.CharField(max_length=100, required=True)
    price_excl_tax = forms.DecimalField(required=True)
    track_file_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = ('title',)
    
    def __init__(self, *args, **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        self.instance.product_class = ProductClass.objects.get(slug='track')

    def clean_track_file_id(self):
        track_file_id = self.cleaned_data['track_file_id']
        if not MediaFile.objects.filter(id=track_file_id).exists():
            raise ValidationError("The file must be uploaded already")
        return track_file_id

    def save(self, commit=True):
        track = super(TrackForm, self).save(commit=False)
        track.attr.author = self.cleaned_data['author']
        track.save()
        partner = Partner.objects.first()
        stock_record, _ = StockRecord.objects.get_or_create(product=track,
                                                            partner=partner,
                                                            partner_sku=track.id
                                                            )
        stock_record.price_excl_tax = self.cleaned_data['price_excl_tax']
        media_file = MediaFile.objects.get(id=self.cleaned_data['track_file_id'])
        stock_record.digital_download = media_file
        stock_record.save()
        return track


BaseTrackFormSet = inlineformset_factory(
    Product, Product, form=TrackForm, extra=2, fk_name='album')


class TrackFormSet(BaseTrackFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(TrackFormSet, self).__init__(*args, **kwargs)
