from django import template
from django.templatetags import static

register = template.Library()


class FullStaticNode(static.StaticNode):
    def url(self, context):
        request = context['request']
        return request.build_absolute_uri(
            super(FullStaticNode, self).url(context)
        )


@register.tag('fullstatic')
def do_static(parser, token):
    return FullStaticNode.handle_token(parser, token)
