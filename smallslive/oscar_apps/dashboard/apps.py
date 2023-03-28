#from oscar.apps.dashboard import config
from oscar.apps.dashboard import apps

class DashboardConfig(apps.DashboardConfig):
    label = 'dashboard'
    name = 'oscar_apps.dashboard'
    verbose_name = 'Dashboard'
