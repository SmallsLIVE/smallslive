from oscar.apps.catalogue import views as catalogue_views
from oscar_apps.catalogue.models import Product


class ProductCategoryView(catalogue_views.ProductCategoryView):
    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['featured_product'] = Product.objects.filter(featured=True, categories=self.get_category()).first()
        return context
