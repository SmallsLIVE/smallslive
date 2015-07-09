from oscar.apps.promotions import views as promotions_views
from oscar_apps.catalogue.models import Product


class HomeView(promotions_views.HomeView):
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['newest_physical_products'] = Product.objects.filter(
            product_class__requires_shipping=True).order_by('-id')[:4]
        context['newest_recordings'] = Product.objects.filter(
            product_class__slug="album").order_by('-id')[:3]
        return context
