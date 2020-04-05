from django.contrib import admin
from django.utils.html import mark_safe
from oscar.apps.catalogue import admin as oscar_admin
from oscar_apps.catalogue.models import UserCatalogue, UserCatalogueProduct
from oscar.core.loading import get_model
from utils.admin import ModelAdminMixin


# Override ProductAdmin

Product = get_model('catalogue', 'Product')
admin.site.unregister(Product)


@admin.register(Product)
class OverrideProductAdmin(oscar_admin.ProductAdmin):
    
    search_fields = ['title']
    list_filter = ['product_class']
    raw_id_fields = ['event', 'event_set', 'artists']


@admin.register(UserCatalogueProduct)
class UserCatalogueProductAdmin(ModelAdminMixin, admin.ModelAdmin):

    raw_id_fields = ['user', 'product']
    search_fields = ['user__first_name', 'user__last_name', 'product__title']
    list_display = ['id', 'user', 'product_column', 'edit_link', 'delete_link']
    list_display_links = ['id']

    def product_column(self, obj):
        return mark_safe('<b>{1}</b> - {0}'.format(obj.product.product_class.name, obj.product.get_title()))
    product_column.short_description = 'Product'
    product_column.strip_tags = False

    def get_queryset(self, request):
        return super(UserCatalogueProductAdmin, self).get_queryset(request) \
            .select_related('product__product_class', 'user')


@admin.register(UserCatalogue)
class UserCatalogueAdmin(admin.ModelAdmin):
    
    raw_id_fields = ['user']
    list_display = ['user', 'has_full_catalogue_access']
    search_fields = ['user__first_name',  'user__last_name', 'user__email']