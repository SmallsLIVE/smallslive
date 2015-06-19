from django import forms
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
    price_excl_tax = forms.DecimalField(required=True)
    track_file = forms.FileField(max_length=400)

    class Meta:
        model = Product
        fields = ('title',)
    
    def __init__(self, *args, **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        self.instance.product_class = ProductClass.objects.get(slug='track')

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
        media_file, _ = MediaFile.objects.get_or_create(media_type='audio', format='mp3',
                                                        file=self.cleaned_data['track_file'])
        stock_record.digital_download = media_file
        stock_record.save()
        return track


BaseTrackFormSet = inlineformset_factory(
    Product, Product, form=TrackForm, extra=2, fk_name='album')


class TrackFormSet(BaseTrackFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(TrackFormSet, self).__init__(*args, **kwargs)
