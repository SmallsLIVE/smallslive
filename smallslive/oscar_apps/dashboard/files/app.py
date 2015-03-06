from django.conf.urls import url

from oscar.core.application import Application
from .views import *


class FilesDashboardApplication(Application):
    name = None
    default_permissions = ['is_staff', ]

    def get_urls(self):
        urls = [
            url(r'^(?P<category>[\w_-]+)/add/$', file_create, name='file-create'),
            url(r'^(?P<category>[\w_-]+)/(?P<pk>\d+)/$', file_edit, name='file-edit'),
            url(r'^(?P<category>[\w_-]+)/(?P<pk>\d+)/delete/$', file_delete, name='file-delete'),
            url(r'^(?P<category>[\w_-]+)/$', file_list, name='file-list'),
        ]
        return self.post_process_urls(urls)


application = FilesDashboardApplication()
