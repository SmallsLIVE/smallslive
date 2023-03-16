#from oscar.apps.dashboard.catalogue import config
from oscar.apps.dashboard.catalogue import apps


class CatalogueDashboardConfig(apps.CatalogueDashboardConfig):
    name = 'oscar_apps.dashboard.catalogue'
