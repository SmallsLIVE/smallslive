from django.contrib import admin
from models import Artist


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('salutation', 'first_name', 'last_name', 'artist_type', 'biography')
    list_display_links = ('salutation', 'first_name', 'last_name')
    list_filter = ('artist_type', 'last_name')
    search_fields = ('first_name', 'last_name')
    save_on_top = True

admin.site.register(Artist, ArtistAdmin)
