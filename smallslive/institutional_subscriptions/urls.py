from django.urls import path, re_path, include
from institutional_subscriptions import views

urlpatterns = [
    re_path(r"^(?P<pk>\d+)/invite-members/$", views.institution_invite_members,
        name="institution_invite_members"),
    re_path(r"^(?P<institution_id>\d+)/uninvite-member/(?P<member_id>\d+)/$", views.institution_member_delete,
        name="institution_uninvite_member"),
    re_path(r"^(?P<pk>\d+)/edit/$", views.institution_edit,
        name="institution_edit"),
    re_path(r"^(?P<pk>\d+)/members/$", views.institution_members,
        name="institution_members"),
    re_path(r"^(?P<pk>\d+)/delete/$", views.institution_delete,
        name="institution_delete"),
    re_path(r"^add/$", views.institution_add,
        name="institution_add"),
    re_path(r'^activate-account/(?P<key>\w+)/$', views.institution_member_activate,
        name='institution_member_confirm_email'),
    re_path(r"^$", views.institution_list,
        name="institution_list"),
]
