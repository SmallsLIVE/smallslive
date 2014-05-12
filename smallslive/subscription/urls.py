from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^$', views.SubscriptionListView.as_view(), name='list'),
                       url(r'^preview/(?P<pk>\d+)/', views.SuccessResponseView.as_view(preview=True),
                           name='paypal-success-response'),
                       url(r'^cancel/', views.CancelResponseView.as_view(),
                           name='paypal-cancel-response'),
                       url(r'^place-order/(?P<pk>\d+)/', views.SuccessResponseView.as_view(),
                           name='paypal-place-order'),
                       url(r'^(?P<pk>\d+)/$', views.SubscriptionDetailView.as_view(),
                           name='detail'),
                       url(r'^(?P<pk>\d+)/buy/$', views.PayPalRedirectView.as_view(), name='buy'),
)
