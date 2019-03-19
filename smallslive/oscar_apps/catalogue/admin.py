from django.contrib import admin

from oscar.apps.catalogue.admin import *  # noqa
from oscar_apps.catalogue.models import UserCatalogue, UserCatalogueProduct


@admin.register(UserCatalogueProduct)
class UserCatalogueProductAdmin(admin.ModelAdmin):

    raw_id_fields = ['user', 'product']
    search_fields = ['user__first_name', 'user__last_name', 'product__title']
    list_display = ['id', 'user', 'product']
    list_display_links = ['id', 'user', 'product']

    def get_queryset(self, request):
        print(type(self))
        return super(UserCatalogueProductAdmin, self).get_queryset(request).select_related('product', 'user')


@admin.register(UserCatalogue)
class UserCatalogueAdmin(admin.ModelAdmin):

    raw_id_fields = ['user']