from django.conf.urls import patterns, include, url


urlpatterns = patterns('multimedia.views',
    url(r"^media-redirect/(?P<recording_id>\d+)/$", 'media_redirect',
        name="media_redirect"),
    url(r"^update_media_viewcount/$", 'update_media_viewcount',
        name="update_media_viewcount"),
    url(r"^most-popular-videos/$", 'most_popular_videos',
        name="most_popular_videos"),
    url(r"^most-recent-videos/$", 'most_recent_videos',
        name="most_recent_videos"),
    url(r"^most-popular-audio/$", 'most_popular_audio',
        name="most_popular_audio"),
    url(r"^most-recent-audio/$", 'most_recent_audio',
        name="most_recent_audio"),
)
