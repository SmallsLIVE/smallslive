from django import template
from django.template import loader

register = template.Library()

@register.simple_tag(takes_context=True)
def offer(context):
    modal = {
        'subscribe': 'become_a_supporter_dialog.html'
    }.get(context.get('offer_modal'))

    if not modal:
        return ''

    context['offer_visible'] = True
    return loader.render_to_string(modal, context_instance=context)
