from django.urls import path, re_path, include
from subscriptions import views

urlpatterns = [
    ## @TODO : Fix later after djstripe upgrade
    # path(r'^sync-payment-history/', sync_payment_history, name='sync_payment_history'),
    path(r'^update-card/', views.update_card, name='update_card'),

    # Turned off the cancel subscriptions for upgrading djstripe to 2.0.0
    re_path(r'^cancel/subscription/$', views.cancel_subscription, name='cancel_subscription'),
    re_path(r'^email-list/', views.subscriber_list_emails, name='subscriber_list_emails'),

    re_path(r'^pledge-update/$', views.update_pledge, name='update_pledge'),
    re_path(r'^reactivate/subscription/$', views.reactivate_subscription,name='reactivate_subscription'),
    re_path(r'^payment-info/$', views.payment_info, name='payment_info'),
    re_path(r'^donation-preview/$', views.donation_preview, name='donation_preview'),
    re_path(r'^supporter/$', views.become_supporter, name='become_supporter'),
    re_path(r'^event-sponsorship/$', views.event_sponsorship, name='event_sponsorship'),
    re_path(r'^gift-support/$', views.gift_support, name='gift_support'),
    re_path(r'^product-support/(?P<product_id>[-\d]+)$', views.product_support, name='product_support'),
    re_path(r'^tickets/$', views.ticket_support, name='ticket_support'),
    re_path(r'^supporter/paypal-execute$', views.supporter_paypal_execute, name='supporter_paypal_execute'),
    re_path(r'^supporter/completed/$', views.become_supporter_complete, name='become_supporter_complete'),
    re_path(r'^donate/$', views.donate, name='donate'),
    re_path(r'^supporter/pending', views.supporter_pending, name='supporter_pending'),
    re_path(r'^supporters-export', views.supporter_list_export, name='supporter_list_export'),
    re_path(r'^supporters/$', views.supporter_list, name='supporter_list'),
    re_path(r'^sponsors/$', views.sponsor_list, name='sponsor_list'),
]
