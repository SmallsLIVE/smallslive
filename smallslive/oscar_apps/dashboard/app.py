from django.conf.urls import url, include

from oscar.apps.dashboard.app import DashboardApplication as CoreDashboardApplication
from oscar.core.loading import get_class


class DashboardApplication(CoreDashboardApplication):
    files_app = get_class('dashboard.files.app', 'application')

    def get_urls(self):
        urls = super(DashboardApplication, self).get_urls()
        urls += [
            url(r'^files/', include(self.files_app.urls)),
        ]
        return self.post_process_urls(urls)


application = DashboardApplication()