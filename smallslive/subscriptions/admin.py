from django.contrib import admin
from .models import Donation


class DonationAdmin(admin.ModelAdmin):

    raw_id_fields = ['user', 'product', 'event']


admin.site.register(Donation, DonationAdmin)

