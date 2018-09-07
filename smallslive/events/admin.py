from django.contrib import admin

from models import Event, Recording, Venue, Comment


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('start', 'venue', 'title', 'subtitle', 'link',
                    'date_freeform', 'description')
    list_display_links = ('title', 'subtitle')
    search_fields = ('title', 'subtitle')
    save_on_top = True

    def save_model(self, request, obj, form, change):
        obj.last_modified_by = request.user
        obj.save()


class CommentAdmin(admin.ModelAdmin):

    list_display = ['id', 'author', 'event_set_id']
    raw_id_fields = ['event_set', 'author']

    def event_set_id(self, obj):
        return obj.event_set.id


admin.site.register(Event, EventAdmin)
admin.site.register(Recording)
admin.site.register(Venue)
admin.site.register(Comment, CommentAdmin)
