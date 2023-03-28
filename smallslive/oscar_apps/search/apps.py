#from oscar.apps.search import config
from oscar.apps.search import apps


class SearchConfig(apps.SearchConfig):
    label = 'search'
    name = 'oscar_apps.search'
    verbose_name = 'Search'
