from django.urls import path
from .views import (
    PublicTimeSlot,
    ReScheduleAppointment,
    ScheduleTime,
    schedule_custom_day_pattern,
    toggle_day_pattern,
    toggle_appt_slot,
    # booking_by_patient,
    book_appointment,
    BookSucceed,
    cancel_appt_by_patient,
    TodayDoctorApptList,
    # ExportApptToPDF,
)
from .feedbackview import feedback_view

app_name = "appointment"
urlpatterns = [
    path("appt/<doctor_id>/", PublicTimeSlot.as_view(), name="public_time_slot"),
    path("appt_reschedule/<doctor_id>/<str:rel>/", ReScheduleAppointment.as_view(), name="reschedule"),
    path("appt/today/<clinic_id>/", TodayDoctorApptList.as_view(), name="doctor_today_appt_list"),
    # path("appt/pdf/<clinic_id>/", ExportApptToPDF.as_view(), name="export_to_pdf"),
    path("schedule/", ScheduleTime.as_view(), name="schedule"),
    path("schedule/custom/", schedule_custom_day_pattern, name="custom_schedule"),
    path("schedule/toggle/day/", toggle_day_pattern, name="toggle_day"),
    path("schedule/toggle/slot/", toggle_appt_slot, name="toggle_appt_slot"),
    # path("booking/patient/slot/", booking_by_patient, name="booking_by_patient"),
    path("booked/", book_appointment, name="book_appointment"),
    path("booked/success/<int:appid>/", BookSucceed.as_view(), name="book_succeed"),
    path("booking/cancel/slot/", cancel_appt_by_patient, name="cancel_appt_by_patient"),
    path("feedback/", feedback_view, name="feedback_view"),
]
