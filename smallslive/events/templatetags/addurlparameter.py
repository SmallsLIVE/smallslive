from django.template import Library, Node, TemplateSyntaxError, Variable

register = Library()


class AddParameter(Node):
    def __init__(self, varname, value):
        self.varname = Variable(varname)
        self.value = Variable(value)

    def render(self, context):
        req = Variable('request').resolve(context)
        params = req.GET.copy()
        final_value = self.value.resolve(context)
        param_name = self.varname.resolve(context)
        url = req.path

        if final_value is not None:
            params[param_name] = final_value
        else:
            if param_name in params:
                del params[param_name]

        if len(params):
            url = '%s?%s' % (req.path, params.urlencode())

        return url


def addurlparameter(parser, token):
    from re import split
    bits = split(r'\s+', token.contents, 2)
    if len(bits) < 2:
        raise TemplateSyntaxError, "'%s' tag requires two arguments" % bits[0]
    return AddParameter(bits[1], bits[2])


register.tag('addurlparameter', addurlparameter)
