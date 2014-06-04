from django.contrib import admin

from models import Event, Set


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('start', 'title', 'subtitle', 'link', 'date_freeform', 'description')
    list_display_links = ('title', 'subtitle')
    search_fields = ('title', 'subtitle')
    save_on_top = True

    def save_model(self, request, obj, form, change):
        obj.last_modified_by = request.user
        obj.save()

admin.site.register(Event, EventAdmin)
admin.site.register(Set)
