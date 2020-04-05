from django.core.urlresolvers import reverse
from artists.models import Artist
from oscar_apps.partner.strategy import Selector
from .models import Product, UserCatalogue, UserCatalogueProduct


class ProductMixin(object):

    def __init__(self):

        self.digital_album_list = []
        self.physical_album_list = []
        self.track_list = []
        self.album_list = []
        self.downloads_list = []

    def get_product_price(self, x):
        selector = Selector()
        strategy = selector.strategy(
            request=self.request, user=self.request.user)

        if x.variants.count():
            price = strategy.fetch_for_product(product=x.variants.first()).price.incl_tax
        else:
            price = strategy.fetch_for_product(product=x).price.incl_tax

        return price

    def get_products(self):

        self.get_purchased_products()
        self.artists_with_media = Artist.objects.exclude(artistproduct=None)
        if self.request.user.is_authenticated():
            self.active_card = self.request.user.get_active_card()

        # Clean basket
        # self.request.basket.flush()

        self.payment_info_url = reverse('payment_info')
        self.donation_preview_url = reverse('donation_preview')

        # TODO: create mixin for gifts so it can be used in become a supporter too.
        self.gifts = []
        self.costs = []

        self.album_product = self.object
        products = Product.objects.filter(parent=self.album_product, product_class__slug__in=[
            'physical-album',
            'digital-album'
        ])
        for product in products:
            self.gifts.append(product)
            if product.variants.count():
                stock = product.variants.first().stockrecords.first()
                self.costs.append(
                    stock.cost_price)
            else:
                stock = product.stockrecords.first()
                if stock:
                    self.costs.append(
                        stock.cost_price)

        variant = Product.objects.filter(parent=self.album_product, product_class__slug__in=[
            'physical-album',
            'digital-album'
        ]).first()

        self.child_product = variant

        self.gifts.sort(
            key=lambda x: self.get_product_price(x))

        self.comma_separated_leaders = self.album_product.get_leader_strings()

    def get_purchased_products(self):
        """ Retrieve products purchased by current user:
            Tracks, CD, or Digital HD. Info comes from the order lines.
            Set up a list of all Albums with Tracks bought.
            CD and HD gives access to all Tracks.

        """
        current_user = self.request.user
        if not current_user.is_authenticated():
            self.album_list = []
            self.downloads_list = []
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
                    'is_bought': True,
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
                total_donation = current_user.get_project_donation_amount(track.product.album.pk)
                if albums_matched:
                    index = albums_matched[0][0]
                    # Add the total donation
                    self.album_list[index]['total_donation'] = total_donation
                else:
                    album_info = {
                        'parent': track.product.album,
                        'is_bought': True,
                        'total_donation': total_donation,
                    }
                    self.album_list.append(album_info)

                self.album_list = sorted(self.album_list, key=lambda k: k['parent'].title)

            self.downloads_list = Product.objects.filter(
                misc_file__isnull=False, access__user=self.request.user)
            self.downloads_list = [x for x in self.downloads_list if x.misc_file.name]


