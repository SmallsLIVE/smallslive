from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    name = 'subscriptions'
    verbose_name = "subscriptions"

    def ready(self):
        from .signals import handlers #noqa
