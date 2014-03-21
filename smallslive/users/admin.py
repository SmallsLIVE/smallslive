from django.contrib import admin
from .models import SmallsUser


class SmallsUserAdmin(admin.ModelAdmin):
    date_hierarchy = 'last_login'
    list_display = ('email', 'access_level', 'login_count', 'subscription_price',
                    'date_joined', 'renewal_date', 'is_active')
    list_filter = ('access_level', 'is_active')
    search_fields = ('email',)
    save_on_top = True

admin.site.register(SmallsUser, SmallsUserAdmin)
