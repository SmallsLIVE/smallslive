from django.urls import path, re_path, include
from subscriptions import views

urlpatterns = [
    ## @TODO : Fix later after djstripe upgrade
    #path(r'^sync-payment-history/', views.sync_payment_history, name='sync_payment_history'),
    #path(r'^update-card/', views.update_card, name='update_card'),
    #path(r'^cancel/subscription/$', views.cancel_subscription, name='cancel_subscription'),
    path(r'^email-list/', views.subscriber_list_emails, name='subscriber_list_emails'),

    path(r'^pledge-update/$', views.update_pledge, name='update_pledge'),
    path(r'^reactivate/subscription/$', views.reactivate_subscription,name='reactivate_subscription'),
    path(r'^payment-info/$', views.payment_info, name='payment_info'),
    path(r'^donation-preview/$', views.donation_preview, name='donation_preview'),
    path(r'^supporter/$', views.become_supporter, name='become_supporter'),
    path(r'^event-sponsorship/$', views.event_sponsorship, name='event_sponsorship'),
    path(r'^gift-support/$', views.gift_support, name='gift_support'),
    path(r'^product-support/(?P<product_id>[-\d]+)$', views.product_support, name='product_support'),
    path(r'^tickets/$', views.ticket_support, name='ticket_support'),
    path(r'^supporter/paypal-execute$', views.supporter_paypal_execute, name='supporter_paypal_execute'),
    path(r'^supporter/completed/$', views.become_supporter_complete, name='become_supporter_complete'),
    path(r'^donate/$', views.donate, name='donate'),
    path(r'^supporter/pending', views.supporter_pending, name='supporter_pending'),
    path(r'^supporters-export', views.supporter_list_export, name='supporter_list_export'),
    path(r'^supporters/$', views.supporter_list, name='supporter_list'),
    path(r'^sponsors/$', views.sponsor_list, name='sponsor_list'),
]
