from django.contrib import admin
from models import Artist, Instrument


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'website','salutation','photo')
    list_display_links = ('first_name', 'last_name')
    list_filter = ('instruments', 'last_name')
    search_fields = ('first_name', 'last_name')
    save_on_top = True


class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')
    list_editable = ('abbreviation',)

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Instrument, InstrumentAdmin)
