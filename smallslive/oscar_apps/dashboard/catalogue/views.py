from oscar.apps.dashboard.catalogue import views as oscar_views
from .forms import TrackFormSet, TrackFileForm


class ProductCreateUpdateView(oscar_views.ProductCreateUpdateView):
    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        self.formsets['track_formset'] = TrackFormSet

    def get_context_data(self, **kwargs):
        context = super(ProductCreateUpdateView, self).get_context_data(**kwargs)
        context['upload_track_form'] = TrackFileForm()
        return context
