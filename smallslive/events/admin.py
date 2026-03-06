from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Event, Recording, Venue, Comment, ShowDefaultTime, JazzCulturalPhotos

admin.site.register(JazzCulturalPhotos)



class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('start', 'state', 'venue', 'title', 'subtitle', 'link',
                    'date_freeform', 'description', 'clonned_from_link', 'root_event')
    list_display_links = ('title', 'subtitle')
    search_fields = ('title', 'subtitle')
    save_on_top = True
    readonly_fields = ('clonned_from_link',)
    exclude = ('clonned_from',)

    def root_event(self, obj):
        root = obj.get_root()
        if root:
            url = reverse("admin:events_event_change", args=[root.pk])
            return format_html('<a href="{}">{}</a>', url, root.title)

    root_event.short_description = "Root Event"

    def clonned_from_link(self, obj):
        if obj.clonned_from:
            url = reverse("admin:events_event_change", args=[obj.clonned_from.pk])
            return format_html('<a href="{}">{}</a>', url, obj.clonned_from.title)
        return "-"
    clonned_from_link.short_description = "Cloned From"

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
        link = reverse('admin:events_event_change', args=[obj.event.id])
        return u'<a href="%s">%s</a>' % (link, obj.event.title)
    link_to_event.allow_tags = True

    def link_to_media_file(self, obj):
        link = reverse('admin:multimedia_media_file_change', args=[obj.media_file.id])
        return u'<a href="%s">%s</a>' % (link, obj.media_file.file)
    link_to_media_file.allow_tags = True


admin.site.register(Recording, RecordingAdmin)
admin.site.register(Venue)
admin.site.register(ShowDefaultTime)


