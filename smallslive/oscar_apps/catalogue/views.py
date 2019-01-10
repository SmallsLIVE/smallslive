from artists.models import Artist
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from oscar.apps.catalogue import views as catalogue_views
from oscar_apps.catalogue.models import Product
from oscar.apps.catalogue.views import ProductCategoryView


class ProductCategoryView(catalogue_views.ProductCategoryView):
    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['featured_product'] = Product.objects.filter(featured=True, categories__in=self.get_categories()).first()
        return context

class ArtistCatalogue(ProductCategoryView):

    def get(self, request, *args, **kwargs):
        id = request.GET.get('id', None)

        artist = Artist.objects.filter(pk=id).first()

        context = {'artist': artist}
        template = 'catalogue/artist-category.html'

        temp = render_to_string(template,
                                context,
                                context_instance=RequestContext(request)
                                )

        data = {
            'template': temp
        }

        return JsonResponse(data)

class ProductDetailView(catalogue_views.ProductDetailView):

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['reviews'] = self.get_reviews()
        ctx['alert_form'] = self.get_alert_form()
        ctx['artist_with_media'] = Artist.objects.exclude(artistproduct=None)
        ctx['has_active_alert'] = self.get_alert_status()
        return ctx
