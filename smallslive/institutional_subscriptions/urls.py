from django.conf.urls import patterns, include, url


urlpatterns = patterns('institutional_subscriptions.views',
    url(r"^(?P<pk>\d+)/invite-members/$", 'institution_invite_members',
        name="institution_invite_members"),
    url(r"^(?P<institution_id>\d+)/uninvite-member/(?P<member_id>\d+)/$", 'institution_member_delete',
        name="institution_uninvite_member"),
    url(r"^(?P<pk>\d+)/edit/$", 'institution_edit',
        name="institution_edit"),
    url(r"^(?P<pk>\d+)/members/$", 'institution_members',
        name="institution_members"),
    url(r"^(?P<pk>\d+)/delete/$", 'institution_delete',
        name="institution_delete"),
    url(r"^add/$", 'institution_add',
        name="institution_add"),
    url(r'^activate-account/(?P<key>\w+)/$', 'institution_member_activate',
        name='institution_member_confirm_email'),
    url(r"^$", 'institution_list',
        name="institutions"),
)
