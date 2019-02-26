from django.db import models
from django.utils.functional import cached_property

from oscar.apps.catalogue.abstract_models import AbstractProduct



class Product(AbstractProduct):
    subtitle = models.CharField(max_length=50, blank=True)
    short_description = models.TextField(blank=True)
    event = models.ForeignKey('events.Event', blank=True, null=True, related_name='products')
    album = models.ForeignKey('self', blank=True, null=True, related_name='tracks')  # used for album/track
    ordering = models.PositiveIntegerField(help_text="Product ordering number, lower numbers come first when ordering",
                                           default=1000)  # explicit ordering, usually for tracks on an album
    preview = models.OneToOneField('multimedia.MediaFile', blank=True, null=True, related_name='product')
    featured = models.BooleanField(default=False, help_text="Make this product featured in the store")

    gift = models.BooleanField(default=False, help_text="Make this product a gift in the store")
    gift_price = models.DecimalField(help_text="Set the gift price",
                                     decimal_places=2, max_digits=12, blank=True, null=True)

    event_set = models.ForeignKey('events.EventSet', related_name='tickets', null=True)
    artist = models.ManyToManyField('artists.Artist', through='ArtistProduct', verbose_name=("Attributes"), blank=True, null=True)

    set = models.CharField(max_length=50, blank=True)

    class Meta(AbstractProduct.Meta):
        ordering = ['ordering', 'title']

    def get_track_preview_url(self):
        if self.preview_id:
            return self.preview.get_file_url()
        else:
            return "blank.mp3"

    @cached_property
    def has_physical_media(self):
        is_album = self.product_class.slug == "album"
        has_physical_child = self.children.filter(product_class__slug="physical-album").exists()
        return is_album and has_physical_child

    @cached_property
    def get_artist_list(self):
        return self.artist.all()

    @cached_property
    def has_digital_media(self):
        is_album = self.product_class.slug == "album"
        has_physical_child = self.children.filter(product_class__slug="digital-album").exists()
        return is_album and has_physical_child

    @cached_property
    def has_tracks(self):
        is_album = self.product_class.slug == "album"
        has_physical_child = self.tracks.exists()
        return is_album and has_physical_child

    @property
    def get_track_stockrecord(self):
        if self.product_class.slug == "track":
            return self.stockrecords.filter(is_hd=False).first()

    @cached_property
    def get_hd_track_stockrecord(self):
        if self.product_class.slug == "track":
            return self.stockrecords.filter(is_hd=True).first()

    def get_product_class(self):
        if self.is_child and self.parent.product_class.slug != "album":
            return self.parent.product_class
        else:
            return self.product_class
    get_product_class.short_description = "Product class"

    def get_tracks(self):
        if self.product_class.slug == 'album':
            return self.tracks.order_by('id')

    def get_title(self):
        """
        Return a product's title or it's parent's title if it has no title
        """
        title = self.title
        if self.parent_id:
            if not self.title:
                title = self.parent.title
            else:
                title = u"{0} ({1})".format(self.parent.title, self.title)
        return unicode(title)

    def _clean_child(self):
        """
        Validates a child product
        """
        if not self.parent_id:
            raise ValidationError(_("A child product needs a parent."))
        if self.parent_id and not self.parent.is_parent:
            raise ValidationError(
                _("You can only assign child products to parent products."))
        if self.pk and self.categories.exists():
            raise ValidationError(
                _("A child product can't have a category assigned."))
        # Note that we only forbid options on product level
        if self.pk and self.product_options.exists():
            raise ValidationError(
                _("A child product can't have options."))

class ArtistProduct(models.Model):
    artist = models.ForeignKey("artists.Artist", verbose_name=(""), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=(""), on_delete=models.CASCADE)
    
    class Meta:
        #abstract = True
        app_label = 'catalogue'
        ordering = ['product', 'artist']
        unique_together = ('product', 'artist')
        verbose_name = ('Artist')
        verbose_name_plural = ('Artist list')


from oscar.apps.catalogue.models import *  # noqa
