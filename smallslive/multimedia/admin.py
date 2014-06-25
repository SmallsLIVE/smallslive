from django.contrib import admin
from .models import MediaFile


class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'media_type', 'format', 'get_file_url')
    list_filter = ('media_type', 'format')


admin.site.register(MediaFile, MediaAdmin)
