from oscar.apps.basket import apps


class BasketConfig(apps.BasketConfig):
    label = 'basket'
    name = 'oscar_apps.basket'
    verbose_name = 'Basket'
