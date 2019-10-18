from stripe.error import APIConnectionError, InvalidRequestError
from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from oscar.apps.catalogue import views as catalogue_views
from oscar_apps.catalogue.models import Product, UserCatalogue, UserCatalogueProduct
from oscar.apps.catalogue.views import ProductCategoryView
from oscar_apps.partner.strategy import Selector
from custom_stripe.models import CustomerDetail
from artists.models import Artist
from users.models import SmallsUser


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
        context = {'artist': artist, 'above_limit': above_limit}
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


class PurchasedProductsInfoMixin(object):

    def __init__(self):

        self.digital_album_list = []
        self.physical_album_list = []
        self.track_list = []
        self.album_list = []

    def get_purchased_products(self):
        """ Retrieve products purchased by current user:
            Tracks, CD, or Digital HD. Info comes from the order lines.
            Set up a list of all Albums with Tracks bought.
            CD and HD gives access to all Tracks.

        """
        if not self.request.user.is_authenticated():
            self.album_list = []
        else:
            catalogue_access = UserCatalogue.objects.filter(user=self.request.user).first()
            if catalogue_access and catalogue_access.has_full_catalogue_access:
                self.digital_album_list = Product.objects.filter(product_class__slug='digital-album')
                self.physical_album_list = Product.objects.filter(product_class__slug='physical-album')
                self.track_list = []
            else:
                self.digital_album_list = Product.objects.filter(
                    product_class__slug='digital-album', access__user=self.request.user)
                self.physical_album_list = Product.objects.filter(
                    product_class__slug='physical-album', access__user=self.request.user)
                self.track_list = UserCatalogueProduct.objects.filter(
                    product__product_class__slug='track', user=self.request.user)
            self.album_list = []
            for album in list(self.digital_album_list) + list(self.physical_album_list):
                album_info = {
                    'parent': album.parent,
                    'bought_tracks': [track.pk for track in album.parent.tracks.all()],
                    'album_type': 'full_album',
                }
                # Avoid duplicates
                album = [a for a in self.album_list if a['parent'] == album.parent]
                if not album:
                    self.album_list.append(album_info)

            # Iterate tracks and accumulate for album
            for track in self.track_list:
                # Search album_list to see if already in list
                # Find the position of the album in the list, if it exists
                albums_matched = [a for a in enumerate(self.album_list)
                                  if a[1]['parent'] == track.product.album]
                if albums_matched:
                    index = albums_matched[0][0]
                    # Add the track to purchased tracks it's not there already.
                    album = albums_matched[0][1]
                    bought_tracks = album['bought_tracks']
                    if track.product.pk not in bought_tracks:
                        bought_tracks.append(track.product.pk)
                        # Update the bought track.
                        self.album_list[index]['bought_tracks'] = bought_tracks
                else:
                    album_info = {
                        'parent': track.product.album,
                        'bought_tracks': [track.product.pk],
                        'album_type': 'track_album',
                    }
                    self.album_list.append(album_info)

                self.album_list = sorted(self.album_list, key=lambda k: k['parent'].title)


class ProductDetailView(catalogue_views.ProductDetailView, PurchasedProductsInfoMixin):

    def can_preview(self, track_list):
        for track in track_list:
            if track.get_track_preview_url() != "blank.mp3":
                return True
        return False

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)

        # We need to clear the basket.
        # Probably do this in a middleware so it's global?
        self.request.basket.flush()

        # Set the flow type for checkout flow
        ctx['flow_type'] = "catalog_selection"

        self.get_purchased_products()
        ctx['reviews'] = self.get_reviews()
        ctx['alert_form'] = self.get_alert_form()
        ctx['artist_with_media'] = Artist.objects.exclude(artistproduct=None)
        ctx['has_active_alert'] = self.get_alert_status()
        ctx['is_catalogue'] = True
        if self.request.user.is_authenticated():
            try:
                customer_detail = CustomerDetail.get(id=self.request.user.customer.stripe_id)
            except APIConnectionError:
                customer_detail = None
            except InvalidRequestError:
                customer_detail = None
            except CustomerDetail.DoesNotExist:
                customer_detail = None
            except SmallsUser.customer.RelatedObjectDoesNotExist:
                customer_detail = None
            if customer_detail:
                ctx['active_card'] = customer_detail.active_card

        if self.object.get_product_class().slug == 'album':
            album_product = Product.objects.filter(pk=self.object.pk ).first()
            ctx['album_product'] = album_product
            ctx['comma_separated_leaders'] = album_product.get_leader_strings()
            track_album = next((item for item in self.album_list if item['parent'] == self.object), None)
            ctx['bought_tracks'] = []
            if track_album:
                ctx['bought_tracks'] = track_album["bought_tracks"]
            ctx['mp3_available'] = album_product.tracks.filter(stockrecords__is_hd=False).count() > 0
            variant = Product.objects.filter(parent=album_product, product_class__slug__in=[
                'physical-album',
                'digital-album'
            ]).first()

            if variant and variant.product_class.slug == 'digital-album':
                for album in self.album_list:
                    if self.object.pk == album["parent"].pk:
                        ctx['is_full'] = "full_album"
            ctx['child_product'] = variant
        ctx['can_preview'] = self.can_preview(album_product.get_tracks())
        print "The preview status is {}".format(ctx['can_preview'])

        # Clean basket
        # self.request.basket.flush()

        ctx['payment_info_url'] = reverse('payment_info')
        ctx['donation_preview_url'] = reverse('donation_preview')
        ctx['product_id'] = self.object.pk

        ctx['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY

        # TODO: create mixin for gifts so it can be used in become a supporter too.
        ctx['gifts'] = []
        ctx['costs'] = []
        selector = Selector()
        strategy = selector.strategy(
            request=self.request, user=self.request.user)

        album_product = Product.objects.filter(pk=self.object.pk).first()
        products = Product.objects.filter(parent=album_product, product_class__slug__in=[
            'physical-album',
            'digital-album'
        ])
        for product in products:
            ctx['gifts'].append(product)
            if product.variants.count():
                stock = product.variants.first().stockrecords.first()
                ctx['costs'].append(
                    stock.cost_price)
            else:
                stock = product.stockrecords.first()
                if stock:
                    ctx['costs'].append(
                        stock.cost_price)

        ctx['gifts'].sort(
            key=lambda x: strategy.fetch_for_product(product=x).price.incl_tax)

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
