from django import forms
from oscar.apps.basket import forms as basket_forms


class AddToBasketForm(basket_forms.AddToBasketForm):
    stockrecord_id = forms.IntegerField(required=False)
