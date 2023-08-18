from django.conf import settings

class CurrentSiteIdMixin(object):
    """
        Mixin to return current site ID
    """
    def get_site_context_data(self, context):
        context['SITE_ID'] = settings.SITE_ID
        return context