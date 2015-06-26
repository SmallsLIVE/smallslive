from oscar.apps.dashboard.catalogue import views as oscar_views
from .forms import TrackFormSet


class ProductCreateUpdateView(oscar_views.ProductCreateUpdateView):
    def get_context_data(self, **kwargs):
        if self.product_class.slug == 'album':
            self.formsets['track_formset'] = TrackFormSet
        return super(ProductCreateUpdateView, self).get_context_data(**kwargs)

    def process_all_forms(self, form):
        if self.product_class.slug == 'album':
            self.formsets['track_formset'] = TrackFormSet
        return super(ProductCreateUpdateView, self).process_all_forms(form)

    form_valid = form_invalid = process_all_forms
