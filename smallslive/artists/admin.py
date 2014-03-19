from django.contrib import admin

from models import Artist

# Register your models here.
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('salutation', 'firstname', 'lastname', 'artist_type', 'biography')
    list_display_links = ('salutation', 'firstname', 'lastname')
    list_filter = ('artist_type', 'lastname')
    search_fields = ('firstname', 'lastname')
    # radio_fields = {'active': admin.HORIZONTAL}
    # filter_horizontal = ('tags', 'speakers',)
    save_on_top = True
    # prepopulated_fields = {'slug': ('title',)}
    # inlines = [RelatedUrlInline]
    # actions = [make_live, make_draft]

admin.site.register(Artist, ArtistAdmin)