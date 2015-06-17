from django import forms
from django.forms import inlineformset_factory
from oscar.apps.dashboard.catalogue import forms as oscar_forms
from oscar.apps.dashboard.catalogue.forms import BaseProductImageFormSet
from oscar_apps.catalogue.models import Product


class ProductForm(oscar_forms.ProductForm):
    class Meta(oscar_forms.ProductForm.Meta):
        fields = [
            'title', 'upc', 'short_description', 'description', 'is_discountable', 'structure']


# class TrackForm(forms.Form):
#     track_no = forms.IntegerField(required=True)
#     title = forms.CharField(max_length=100, required=True)
#     author = forms.CharField(max_length=100, required=True)
#
#
# BaseTrackFormSet = inlineformset_factory(
#     Product, Product, form=TrackForm, extra=2)
#
#
# class TrackFormSet(BaseProductImageFormSet):
#
#     def __init__(self, product_class, user, *args, **kwargs):
#         super(TrackFormSet, self).__init__(*args, **kwargs)
