from django.urls import reverse
from django.utils.safestring import mark_safe


class ModelAdminMixin(object):

    @staticmethod
    def get_link_url(obj, action, args=None, kwargs=None):
        url = 'admin:{app}_{model}_{action}'.format(
            app=obj._meta.app_label,
            model=obj._meta.model_name,
            action=action)
        return reverse(url, args=args, kwargs=kwargs)

    @staticmethod
    def get_delete_link_url(obj):
        return ModelAdminMixin.get_link_url(obj, 'delete', args=[obj.id])

    def delete_link(self, obj):
        return mark_safe('<a href="{url}">{action}</a>'.format(
            action='Delete',
            url=ModelAdminMixin.get_delete_link_url(obj)))
    delete_link.short_description = ''

    @staticmethod
    def get_edit_link_url(obj):
        return ModelAdminMixin.get_link_url(obj, 'change', args=[obj.id])

    def edit_link(self, obj):
        return mark_safe('<a href="{url}">{action}</a>'.format(
            action='Edit',
            url=ModelAdminMixin.get_edit_link_url(obj)))
    edit_link.short_description = ''
