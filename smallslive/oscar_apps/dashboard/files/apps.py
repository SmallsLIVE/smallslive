from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FilesDashboardConfig(AppConfig):
    label = 'files_dashboard'
    name = 'oscar_apps.dashboard.files'
    verbose_name = _('Files dashboard')
    default_permissions = ['is_staff', ]

    def get_urls(self):
        urls = [
            url(r'^(?P<category>[\w_-]+)/add/$', file_create, name='file-create'),
            url(r'^(?P<category>[\w_-]+)/(?P<pk>\d+)/$', file_edit, name='file-edit'),
            url(r'^(?P<category>[\w_-]+)/(?P<pk>\d+)/delete/$', file_delete, name='file-delete'),
            url(r'^(?P<category>[\w_-]+)/$', file_list, name='file-list'),
        ]
        return self.post_process_urls(urls)
