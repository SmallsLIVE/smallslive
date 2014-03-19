from django.contrib import admin

from models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    date_hierarchy = 'last_login'
    list_display = ('user', 'access_level', 'login_count', 'subscription_price', 'start_date', 'renewal_date', 'active')
    list_filter = ('access_level', 'active')
    search_fields = ('user',)
    # radio_fields = {'active': admin.HORIZONTAL}
    # filter_horizontal = ('tags', 'speakers',)
    save_on_top = True
    # prepopulated_fields = {'slug': ('title',)}
    # inlines = [RelatedUrlInline]
    # actions = [make_live, make_draft]

admin.site.register(UserProfile, UserProfileAdmin)