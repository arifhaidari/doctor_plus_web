from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Blogger,
    HealthMinistry,
    Doctor,
    DoctorTitle,
    Speciality,
    SpecialityCategory,
    Service,
    Patient,
    Relative,
    BloodGroup,
    Condition,
    RelativeRelation,
    FreeServiceSchedule, 
    OTPVerification
)

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    list_display = ("full_name", "phone", "date_of_birth", "gender", "timestamp", "user_type", "active", "suspend")
    list_filter = ("gender", "user_type", "active")
    fieldsets = [
        (None, {"fields": ("full_name", "rtl_full_name", "date_of_birth", "user_type", "gender", "avatar")}),
        ("Credential", {"fields": ("phone", "email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "admin",
                    "staff",
                    "active",
                    "suspend",
                )
            },
        ),
    ]
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("phone", "password1", "password2")}),)
    search_fields = (
        "phone",
        "full_name",
    )
    ordering = ("-timestamp",)
    filter_horizontal = ()


class DoctorTitleAdmin(admin.ModelAdmin):
    list_display = ("title", "farsi_title", "pashto_title")


class SpecialityCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "farsi_name", "pashto_name", "icon")
    search_fields = ("name", "farsi_name", "pashto_name")
    ordering = ("name",)


class ServiceInline(admin.TabularInline):
    model = Service
    min_num = 1
    extra = 0
    # max_num = 100
    # raw_id_fields = ("speciality",)


class ConditionInline(admin.TabularInline):
    model = Condition
    min_num = 1
    extra = 0
    # max_num = 100
    # raw_id_fields = ("speciality",)


class SpecialityAdmin(admin.ModelAdmin):
    inlines = [ConditionInline, ServiceInline]
    list_display = ("name", "farsi_name", "pashto_name", "speciality_category")
    search_fields = ("name", "farsi_name", "pashto_name")
    ordering = ("name",)
    list_filter = ("speciality_category",)


class DoctorAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "doc_license_no", "fee", "professional_status")
    autocomplete_fields = [
        "speciality",
    ]
    search_fields = ("user", "speciality")
    list_editable = ("fee", "professional_status")
    ordering = ("title",)
    list_filter = ("title", "speciality")


class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "blood_group")
    # list_display = ('user.phone', 'blood_group')
    list_display_links = ("user", "blood_group")
    search_fields = ("user", "blood_group")
    ordering = ("user",)
    list_filter = ("blood_group",)


class RelativeAdmin(admin.ModelAdmin):
    list_display = ("user", "patient", "relation", "blood_group")
    search_fields = ("user", "patient", "blood_group")
    ordering = ("user", "patient")
    list_filter = ("blood_group",)


admin.site.register(DoctorTitle, DoctorTitleAdmin)
admin.site.register(SpecialityCategory, SpecialityCategoryAdmin)
admin.site.register(Speciality, SpecialityAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Relative, RelativeAdmin)
admin.site.register(Blogger)
admin.site.register(HealthMinistry)
admin.site.register(BloodGroup)
admin.site.register(FreeServiceSchedule)
admin.site.register(RelativeRelation)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(OTPVerification)
