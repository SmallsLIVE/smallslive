from django.contrib import admin

from models import Event


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_day'
    list_display = ('start_day', 'title', 'subtitle', 'link', 'date_freeform', 'description')
    list_display_links = ('title', 'subtitle')
    search_fields = ('title', 'subtitle')
    save_on_top = True

    def save_model(self, request, obj, form, change):
        obj.last_modified_by = request.user
        obj.save()

admin.site.register(Event, EventAdmin)