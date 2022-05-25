from django.contrib import admin

from .models import Appointment, WeekDays, DaySchedulePattern, DeactivatedApptSlot, ApptQrCode
from .models import Feedback, FeedbackReplies, ApptConditionTreat


class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "patient_or_relative",
        "clinic",
        "start_appt_time",
        "end_appt_time",
        "day_pattern",
        "appt_duration",
        "appt_date",
        "active",
        "status",
    )
    search_fields = ("id", "doctor__user__full_name", "patient__user__full_name", "relative__user__full_name")
    ordering = ("day_pattern", "start_appt_time")
    list_filter = ("status", "feedback", "appt_date", "active", "clinic", "day_pattern")

    def patient_or_relative(self, obj):
        if obj.patient and obj.relative is None:
            return obj.patient
        return obj.relative

    def appt_duration(self, obj):
        if obj.start_appt_time and obj.end_appt_time:
            return str(obj.end_appt_time - obj.start_appt_time)
        return ""


class InlineFeedbackRely(admin.TabularInline):
    model = FeedbackReplies
    extra = 0


class FeedbackAdmin(admin.ModelAdmin):
    inlines = [InlineFeedbackRely]
    list_display = ("appointment", "overall_experience", "doctor_checkup", "staff_behavior", "clinic_environment")
    search_fields = ("appointment", "comment")
    ordering = ("-appointment__appt_date",)
    list_filter = ("overall_experience", "doctor_checkup", "staff_behavior", "clinic_environment")


class DaySchedulePatternAdmin(admin.ModelAdmin):
    list_display = ("week_day", "time_slot_duration", "start_day_time", "end_day_time", "doctor", "clinic")
    search_fields = ("week_day", "doctor", "clinic")
    ordering = ("week_day", "start_day_time")
    list_filter = ("week_day", "active", "clinic", "doctor")


class DeactivatedApptSlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "clinic", "day_pattern", "start_appt_time", "end_appt_time")
    search_fields = ("doctor", "clinic", "day_pattern")
    ordering = ("day_pattern", "start_appt_time")
    list_filter = ("day_pattern", "clinic", "doctor")


class ApptQrCodeAdmin(admin.ModelAdmin):
    # list_display = ("appt_slot", "doctor", "patient_or_relative", "clinic", "qr_code_img")
    # search_fields = ("doctor", "clinic")
    # ordering = ("appt_slot", "doctor")
    # list_filter = ("doctor", "clinic", "patient", "relative")
    list_display = ("appt_slot",)

    def patient_or_relative(self, obj):
        if obj.patient:
            return obj.patient
        return obj.relative


@admin.register(ApptConditionTreat)
class ApptConditionTreat(admin.ModelAdmin):
    list_display = ("id", "name", "farsi_name", "pashto_name")
    search_fields = ("name", "farsi_name", "pashto_name")


admin.site.register(FeedbackReplies)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(DeactivatedApptSlot, DeactivatedApptSlotAdmin)
admin.site.register(DaySchedulePattern, DaySchedulePatternAdmin)
admin.site.register(ApptQrCode, ApptQrCodeAdmin)
admin.site.register(WeekDays)
