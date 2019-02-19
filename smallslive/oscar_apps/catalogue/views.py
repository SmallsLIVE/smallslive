from artists.models import Artist
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render
from oscar.apps.catalogue import views as catalogue_views
from oscar_apps.catalogue.models import Product
from oscar.apps.catalogue.views import ProductCategoryView
from oscar.apps.order.models import Line
from django.db.models import F, Q, Max



class ProductCategoryView(catalogue_views.ProductCategoryView):
    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['featured_product'] = Product.objects.filter(featured=True, categories__in=self.get_categories()).first()
        return context


class ArtistCatalogue(ProductCategoryView):

    def get(self, request, *args, **kwargs):
        id = request.GET.get('id', None)

        artist = Artist.objects.filter(pk=id).first()
        above_limit = artist.albums().count() > 8
        context = {'artist': artist, 'above_limit':above_limit}
        template = 'catalogue/artist-category.html'

        temp = render_to_string(template,
                                context,
                                context_instance=RequestContext(request)
                                )

        data = {
            'template': temp
        }

        return JsonResponse(data)


def get_album_catalog(request):
    template = 'catalogue/album-list.html'
    artist_id = request.GET.get('artist', '')
    if artist_id:
        artist = Artist.objects.filter(pk=artist_id).first()
        album_list = artist.albums()
        artist_page = True
    else:
        album_list =  Product.objects.filter(product_class__name="Album")
        artist_page = False
    paginator = Paginator(album_list, 12)
    page = int(request.GET.get('page', 1))
    album_page = paginator.page(page)
    temp = render_to_string(
        template,
        {'album_page': album_page, 'pagenumber': page, 'artist_page': artist_page},
        context_instance=RequestContext(request))

    data = {
        'template': temp, 'last_page': paginator.num_pages == page
    }

    return JsonResponse(data)


class ProductDetailView(catalogue_views.ProductDetailView):

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['reviews'] = self.get_reviews()
        ctx['alert_form'] = self.get_alert_form()
        ctx['artist_with_media'] = Artist.objects.exclude(artistproduct=None)
        ctx['has_active_alert'] = self.get_alert_status()
        if self.object.get_product_class().slug == 'album':
            ctx['album_product'] = Product.objects.filter(pk = self.object.pk ).first()


            digital_album_list = Line.objects.select_related('product', 'stockrecord', 'product__event', 'product__album').filter( Q(product__product_class__slug='digital-album'),order__user=self.request.user).distinct('stockrecord')
            track_list = Line.objects.select_related('product', 'stockrecord', 'product__event', 'product__album').filter(Q(
                product__product_class__slug='track') ,
                order__user=self.request.user).distinct('stockrecord')
            album_list = []
            ##pass full albums
            for album in digital_album_list:
                album_list.append(album.product.parent.pk)

            ##pass tracks to album    
            track_to_album_list = []
            album = {"parent":None,"bought_tracks":[]}
            last_parent_id = 0
            for track in track_list:
                track_parent_id = track.product.album.pk
                if track_parent_id == last_parent_id:
                    album["bought_tracks"].append(track.product.pk)
                else:
                    if album["parent"] == None:
                        album = {"parent":track.product.album.pk,"bought_tracks":[track.product.pk],"album_type":"track_album"}
                    else:
                        track_to_album_list.append(album)
                        album = {"parent":track.product.album.pk,"bought_tracks":[track.product.pk],"album_type":"track_album"}
                last_parent_id = track_parent_id
            track_to_album_list.append(album)
            track_album = next((item for item in track_to_album_list if item["parent"] == self.object.pk),None)
            ctx['bought_tracks'] = None
            if track_album:
                ctx['bought_tracks'] = track_album["bought_tracks"]
            
            ctx['is_full'] = self.object.pk in album_list


        return ctx


    def get_template_names(self):
        """
        Return a list of possible templates.

        If an overriding class sets a template name, we use that. Otherwise,
        we try 2 options before defaulting to catalogue/detail.html:
            1). detail-for-upc-<upc>.html
            2). detail-for-class-<classname>.html

        This allows alternative templates to be provided for a per-product
        and a per-item-class basis.
        """ 
        if self.object.get_product_class().slug == 'album':
            return ['multimedia/store-album.html']

        if self.template_name:
            return [self.template_name]

        return [
            '%s/detail-for-upc-%s.html' % (
                self.template_folder, self.object.upc),
            '%s/detail-for-class-%s.html' % (
                self.template_folder, self.object.get_product_class().slug),
            '%s/detail.html' % (self.template_folder)]