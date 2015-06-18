from django import forms
from django.forms import inlineformset_factory
from oscar.apps.dashboard.catalogue import forms as oscar_forms
from oscar_apps.catalogue.models import Product, ProductClass


class ProductForm(oscar_forms.ProductForm):
    class Meta(oscar_forms.ProductForm.Meta):
        fields = [
            'title', 'upc', 'short_description', 'description', 'is_discountable', 'structure']


class TrackForm(forms.ModelForm):
    track_no = forms.IntegerField(required=True)
    title = forms.CharField(max_length=100, required=True)
    author = forms.CharField(max_length=100, required=True)
    price_excl_tax = forms.CharField(max_length=100, required=True)

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


BaseTrackFormSet = inlineformset_factory(
    Product, Product, form=TrackForm, extra=2, fk_name='album')


class TrackFormSet(BaseTrackFormSet):

    def __init__(self, product_class, user, *args, **kwargs):
        super(TrackFormSet, self).__init__(*args, **kwargs)
