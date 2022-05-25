from django.contrib import admin
import nested_admin

from .models import  MedicalRecords, MedicalRecordFile

# admin.site.register(FileSharingPatient)
admin.site.register(MedicalRecords)
admin.site.register(MedicalRecordFile)

# Register your models here.
# class InlineMedicalRecord2(nested_admin.NestedTabularInline):
#     model = MedicalRecordFile
#     extra = 0


# class InlineMedicalRecord(nested_admin.NestedTabularInline):
#     model = MedicalRecords
#     extra = 0
#     inlines = [InlineMedicalRecord2]
    

# @admin.register(FileSharingPatient)
# class FileSharingPatientAdmin(nested_admin.NestedModelAdmin):
#     inlines = [InlineMedicalRecord]
#     list_display = ("id", "patient", "relative")
#     list_display_links = ("id", "patient")
#     search_fields = ("id", "patient", "doctor")
#     # ordering = ("-timestamp",)
#     list_filter = ("patient__user__gender", "patient__blood_group")


"""
*** django-nested-admin 3.3.3 ***
app: nested_admin
-------------------------------------
django.contrib.admin    nested_admin
ModelAdmin              NestedModelAdmin
InlineModelAdmin        NestedInlineModelAdmin
StackedInline           NestedStackedInline
TabularInline           NestedTabularInline
"""
