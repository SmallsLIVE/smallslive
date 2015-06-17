from oscar.apps.dashboard.catalogue import views as oscar_views
#from .forms import TrackFormSet


class ProductCreateUpdateView(oscar_views.ProductCreateUpdateView):
    def __init__(self, *args, **kwargs):
        super(ProductCreateUpdateView, self).__init__(*args, **kwargs)
        #self.formsets['track_formset'] = TrackFormSet
