from django.conf.urls import patterns, include, url


urlpatterns = patterns('multimedia.views',
    url(r"^update_media_viewcount/$", 'update_media_viewcount',
        name="update_media_viewcount"),
)
