from django.contrib import admin
from django.core import urlresolvers
from models import Event, Recording, Venue, Comment, ShowDefaultTime


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('start', 'state', 'venue', 'title', 'subtitle', 'link',
                    'date_freeform', 'description')
    list_display_links = ('title', 'subtitle')
    search_fields = ('title', 'subtitle')
    save_on_top = True

    def save_model(self, request, obj, form, change):
        obj.last_modified_by = request.user
        obj.save()


admin.site.register(Event, EventAdmin)


class CommentAdmin(admin.ModelAdmin):

    list_display = ['id', 'author', 'event_set_id']
    raw_id_fields = ['event_set', 'author']

    def event_set_id(self, obj):
        return obj.event_set.id

admin.site.register(Comment, CommentAdmin)


class RecordingAdmin(admin.ModelAdmin):

    list_display = (
        'link_to_media_file',
        'link_to_event',
        'title',
        'set_number',
        'state',
        'date_added',
        'view_count',
    )

    def link_to_event(self, obj):
        link = urlresolvers.reverse('admin:events_event_change', args=[obj.event.id])
        return u'<a href="%s">%s</a>' % (link, obj.event.title)
    link_to_event.allow_tags = True

    def link_to_media_file(self, obj):
        link = urlresolvers.reverse('admin:multimedia_media_file_change', args=[obj.media_file.id])
        return u'<a href="%s">%s</a>' % (link, obj.media_file.file)
    link_to_media_file.allow_tags = True


admin.site.register(Recording, RecordingAdmin)
admin.site.register(Venue)
admin.site.register(ShowDefaultTime)


