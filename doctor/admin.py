from django.contrib import admin
from django.db import models
from .models import (
    DoctorAttachment,
    Clinic,
    Education,
    Experience,
    DoctorProfileView,
    SocialMedia,
    MedicalCondition,
    Disease,
    Symptoms,
    Award,
    EducationDegree,
    DegreeType
)


class ClinicAdmin(admin.ModelAdmin):
    list_display = ("clinic_name", "city", "district")
    search_fields = ("city",)
    ordering = ("city",)
    list_filter = ("city",)


class EducationDegreeAdmin(admin.ModelAdmin):
    list_display = ("name", "farsi_name", "pashto_name")
    search_fields = ("name", "farsi_name", "pashto_name")
    # ordering = ("degree_type",)

class EducationAdmin(admin.ModelAdmin):
    list_display = ("doctor", "school_name", "degree", "start_date", "end_date")
    search_fields = ("doctor", "school_name", "degree")
    ordering = ("doctor",)


class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("doctor", "hospital_name", "designation", "start_date", "end_date")
    search_fields = ("doctor", "hospital_name", "designation")
    ordering = ("doctor",)


class AwardAdmin(admin.ModelAdmin):
    list_display = ("doctor", "award_name", "rtl_award_name", "award_year")
    search_fields = ("doctor", "award_name", "rtl_award_name")
    ordering = ("doctor",)


class DoctorProfileViewAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "counter", "datestamp")
    search_fields = ("doctor", "patient")
    ordering = ("counter",)


class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ("doctor", "facebook", "whatsapp")
    search_fields = ("doctor", "facebook")


class MedicalConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "farsi_name", "pashto_name", "speciality")
    search_fields = ("name", "farsi_name", "pashto_name")
    ordering = ("name",)
    list_filter = ("speciality",)


class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("name", "farsi_name", "pashto_name")
    search_fields = ("name", "farsi_name", "pashto_name")
    ordering = ("name",)
    list_filter = ("speciality",)


@admin.register(Symptoms)
class SymptomsAdmin(admin.ModelAdmin):
    list_display = ("name", "farsi_name", "pashto_name")
    search_fields = ("name", "farsi_name", "pashto_name")
    ordering = ("name",)
    list_filter = ("disease",)


admin.site.register(DoctorAttachment)
admin.site.register(DegreeType)
admin.site.register(Clinic, ClinicAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(DoctorProfileView, DoctorProfileViewAdmin)
admin.site.register(SocialMedia, SocialMediaAdmin)
admin.site.register(MedicalCondition, MedicalConditionAdmin)
admin.site.register(Disease, DiseaseAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(EducationDegree, EducationDegreeAdmin)
