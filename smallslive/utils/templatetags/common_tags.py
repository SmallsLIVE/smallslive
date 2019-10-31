import datetime
from django import template
from django.utils import timezone


register = template.Library()


@register.simple_tag
def get_today_and_tomorrow_dates(date_format):
    now_ny = timezone.localtime(timezone.now())
    if now_ny.hour <= 5:
        today = now_ny - datetime.timedelta(days=1)
    else:
        today = now_ny
    tomorrow = today + datetime.timedelta(days=1)

    return '{} - {}'.format(today.strftime(date_format),
                            tomorrow.strftime(date_format))
