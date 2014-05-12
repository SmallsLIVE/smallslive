from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.db import models
from django.template.response import TemplateResponse
from django.utils.html import conditional_escape as esc
from django.utils.translation import ugettext as _
from models import Subscription, UserSubscription, ExpressTransaction, SubscriptionFeature, Feature


def _pricing(sub): return sub.get_pricing_display()


def _trial(sub): return sub.get_trial_display()


class FeatureAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'class':'form-control'})},
    }

admin.site.register(Feature, FeatureAdmin)


class SubscriptionFeatureAdmin(admin.StackedInline):
    model = SubscriptionFeature
    modal = True


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', _pricing, _trial, 'best_choice',)
    inlines = (SubscriptionFeatureAdmin,)

    def get_urls(self):
        urls = super(SubscriptionAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^plans/$', self.admin_site.admin_view(self.plans_view), name='plans'),
        )
        return my_urls + urls

    def plans_view(self, request):
        context = {
            'features': Feature.objects.all(),
            'plans': self.queryset(request),
        }

        return TemplateResponse(request,
            'admin/subscription/subscription_list.html'
        , context, current_app=self.admin_site.name)
    _pricing.short_description = _(u"pricing")
    _trial.short_description = _(u"trial")


admin.site.register(Subscription, SubscriptionAdmin)


def _subscription(trans):
    return u'<a href="/admin/subscription/subscription/%d/">%s</a>' % (
        trans.subscription.pk, esc(trans.subscription) )


_subscription.allow_tags = True


def _user(trans):
    return u'<a href="/admin/auth/user/%d/">%s</a>' % (
        trans.user.pk, esc(trans.user) )


_user.allow_tags = True


class UserSubscriptionAdminForm(forms.ModelForm):
    class Meta:
        model = UserSubscription

    fix_group_membership = forms.fields.BooleanField(required=False)
    extend_subscription = forms.fields.BooleanField(required=False)


class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ( '__unicode__', _user, _subscription, 'active', 'start', 'expires', 'valid', 'cancelled')
    list_display_links = ( '__unicode__', )
    list_filter = ('active', 'subscription', )
    date_hierarchy = 'expires'
    form = UserSubscriptionAdminForm
    fieldsets = (
        (None, {'fields': ('user', 'subscription', 'expires', 'active')}),
        ('Actions', {'fields': ('fix_group_membership', 'extend_subscription'),
                     'classes': ('collapse',)}),
    )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data['extend_subscription']:
            obj.extend()
        if form.cleaned_data['fix_group_membership']:
            obj.fix()
        obj.save()

    # action for Django-SVN or django-batch-admin app
    actions = ( 'fix', 'extend', )

    def fix(self, request, queryset):
        for us in queryset.all():
            us.fix()

    fix.short_description = 'Fix group membership'

    def extend(self, request, queryset):
        for us in queryset.all(): us.extend()

    extend.short_description = 'Extend subscription'


admin.site.register(UserSubscription, UserSubscriptionAdmin)


class ExpressTransactionAdmin(admin.ModelAdmin):
    list_display = ['method', 'amount', 'currency', 'correlation_id', 'ack', 'token',
                    'date_created']
    readonly_fields = [
        'method',
        'version',
        'amount',
        'currency',
        'ack',
        'correlation_id',
        'token',
        'error_code',
        'error_message',
        'raw_request',
        'raw_response',
        'response_time',
        'date_created',
        'request',
        'response']


admin.site.register(ExpressTransaction, ExpressTransactionAdmin)