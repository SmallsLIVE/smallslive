import itertools
from django.db.models import Count
from oscar.apps.promotions import views as promotions_views
from oscar_apps.catalogue.models import Product
from artists.models import Artist


class HomeView(promotions_views.HomeView):
    """"""
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['newest_recordings'] = Product.objects.filter(
            product_class__slug="album").order_by('-id')[:12]
        context['all_recordings'] = Product.objects.filter(
            product_class__slug="album")[:12]
        context['featured_recordings'] = Product.objects.filter(
            product_class__slug="album", featured=True)[:4]
        context['featured_physical_products'] = Product.objects.filter(
            product_class__slug="merchandise", featured=True)[:4]
        context['preview_track_id_counter'] = itertools.count()
        context['artist_with_media'] = Artist.objects.exclude(artistproduct=None) 
        context['above_limit'] = Product.objects.filter(product_class__slug="album").count() > 8

        return context
