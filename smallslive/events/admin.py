from django.contrib import admin

from models import Event

# Register your models here.

class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'startday'
    list_display = ('startday', 'title', 'subtitle', 'link', 'datefreeform', 'description')
    list_filter = ('title',)
    search_fields = ('title', 'subtitle')
    # radio_fields = {'active': admin.HORIZONTAL}
    # filter_horizontal = ('tags', 'speakers',)
    save_on_top = True
    # prepopulated_fields = {'slug': ('title',)}
    # inlines = [RelatedUrlInline]
    # actions = [make_live, make_draft]

admin.site.register(Event, EventAdmin)