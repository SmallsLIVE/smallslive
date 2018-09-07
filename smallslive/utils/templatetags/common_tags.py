from django import template
import datetime

register = template.Library()


@register.simple_tag
def tomorrow(date_format):
    next_day = datetime.date.today() + datetime.timedelta(days=1)
    return next_day.strftime(date_format)
