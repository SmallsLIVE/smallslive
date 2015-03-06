from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class


class FilesDashboardApplication(Application):
    name = None
    default_permissions = ['is_staff', ]

    press_file_create_view = get_class('dashboard.files.views', 'PressFileCreateView')
    press_file_update_view = get_class('dashboard.files.views', 'PressFileUpdateView')
    press_file_delete_view = get_class('dashboard.files.views', 'PressFileDeleteView')
    press_file_list_view = get_class('dashboard.files.views', 'PressFileListView')

    press_photo_create_view = get_class('dashboard.files.views', 'PressPhotoCreateView')
    press_photo_update_view = get_class('dashboard.files.views', 'PressPhotoUpdateView')
    press_photo_delete_view = get_class('dashboard.files.views', 'PressPhotoDeleteView')
    press_photo_list_view = get_class('dashboard.files.views', 'PressPhotoListView')

    def get_urls(self):
        urls = [
            url(r'^press-photos/add/$', self.press_photo_create_view.as_view(), name='press-photo-create'),
            url(r'^press-photos/(?P<pk>\d+)/$', self.press_photo_update_view.as_view(), name='press-photo'),
            url(r'^press-photos/(?P<pk>\d+)/delete/$', self.press_photo_delete_view.as_view(), name='press-photo-delete'),
            url(r'^press-photos/$', self.press_photo_list_view.as_view(), name='press-photo-list'),
            url(r'^press-files/add/$', self.press_file_create_view.as_view(), name='press-file-create'),
            url(r'^press-files/(?P<pk>\d+)/$', self.press_file_update_view.as_view(), name='press-file'),
            url(r'^press-files/(?P<pk>\d+)/delete/$', self.press_file_delete_view.as_view(), name='press-file-delete'),
            url(r'^press-files/$', self.press_file_list_view.as_view(), name='press-file-list'),
        ]
        return self.post_process_urls(urls)


application = FilesDashboardApplication()
