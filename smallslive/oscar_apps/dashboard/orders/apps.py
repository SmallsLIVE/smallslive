import oscar.apps.dashboard.orders.apps as apps


class OrdersDashboardConfig(apps.OrdersDashboardConfig):
    label = 'orders_dashboard'
    name = 'oscar_apps.dashboard.orders'
    verbose_name = 'Orders dashboard'
