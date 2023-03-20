from django.urls import path, re_path, include
from subscriptions import views

urlpatterns = [
    ## @TODO : Fix later after djstripe upgrade
    #path(r'^sync-payment-history/', views.sync_payment_history, name='sync_payment_history'),
    path(r'^email-list/', views.subscriber_list_emails, name='subscriber_list_emails'),
    path(r'^update-card/', views.update_card, name='update_card'),
    path(r'^cancel/subscription/$', views.cancel_subscription,name='cancel_subscription'),
    path(r'^pledge-update/$', views.update_pledge, name='update_pledge'),
    path(r'^reactivate/subscription/$', reactivate_subscription,name='reactivate_subscription'),
    path(r'^payment-info/$', payment_info, name='payment_info'),
    path(r'^donation-preview/$', donation_preview, name='donation_preview'),
    path(r'^supporter/$', become_supporter, name='become_supporter'),
    path(r'^event-sponsorship/$', event_sponsorship, name='event_sponsorship'),
    path(r'^gift-support/$', gift_support, name='gift_support'),
    path(r'^product-support/(?P<product_id>[-\d]+)$', product_support, name='product_support'),
    path(r'^tickets/$', ticket_support, name='ticket_support'),
    path(r'^supporter/paypal-execute$', supporter_paypal_execute, name='supporter_paypal_execute'),
    path(r'^supporter/completed/$', become_supporter_complete, name='become_supporter_complete'),
    path(r'^donate/$', donate, name='donate'),
    path(r'^supporter/pending', supporter_pending, name='supporter_pending'),
    path(r'^supporters-export', supporter_list_export, name='supporter_list_export'),
    path(r'^supporters/$', supporter_list, name='supporter_list'),
    path(r'^sponsors/$', sponsor_list, name='sponsor_list'),
]
