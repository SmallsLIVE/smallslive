from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FilesDashboardConfig(AppConfig):
    label = 'files_dashboard'
    name = 'oscar_apps.dashboard.files'
    verbose_name = _('Files dashboard')
