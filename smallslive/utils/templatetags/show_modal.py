from django import template
from django.template import loader

register = template.Library()


@register.simple_tag(takes_context=True)
def show_modal(context):
    modal = {
        'email_confirmed': 'email_confirmed_dialog.html'
    }.get(context.get('show_modal'))

    if not modal:
        return ''

    context['modal_visible'] = True
    return loader.render_to_string(modal, context_instance=context)
