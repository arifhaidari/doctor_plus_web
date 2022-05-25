from django.contrib import admin

from .models import Language, City, District, Payment, DoctorSocialMedia, SocialMedia, Address


class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "rtl_name")


class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "rtl_name", "city")
    search_fields = ("name", "rtl_name", "city")
    ordering = ("city",)
    list_filter = ("city",)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("doctor", "amount", "balance", "received_amount", "pay_date", "start_date", "end_date")
    search_fields = ("doctor",)


class DoctorSocialMediaAdmin(admin.ModelAdmin):
    list_display = ("doctor", "social_media", "social_media_url")
    search_fields = ("doctor", "social_media")
    ordering = ("doctor", "social_media")
    list_filter = ("social_media",)


class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "district")
    search_fields = ("city", "district")
    list_filter = ("city",)
    ordering = ("city",)


admin.site.register(Language)
admin.site.register(SocialMedia)
admin.site.register(City, CityAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(DoctorSocialMedia, DoctorSocialMediaAdmin)
admin.site.register(Address, AddressAdmin)
