from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views as v

from django.urls import include

# router = DefaultRouter()
# router.register("doctor", v.DoctorViewSet, basename="doctor")
# router.register("award", v.AwardViewSet, basename="award")
# router.register("education", v.EducationViewSet, basename="education")
# router.register("experience", v.ExperienceViewSet, basename="experience")

# router.register("clinic", v.ClinicViewSet, basename="clinic")
# router.register("feedback", v.FeedbackViewSet, basename="feedback")
# router.register("feedback_reply", v.FeedbackRepliesViewSet, basename="feedback_reply")
# router.register("notification", v.NotificationViewSet, basename="noti")
# router.register("medicalrecord", v.MedicalRecordViewSet, basename="medicalrecord")
# router.register("appointment", v.AppointmentViewSet, basename="appointment")
# #
# # router.register("daypattren", v.DaySchedulePatternViewSet, basename="day")
# router.register("deactivedslot", v.DeactivatedApptSlotViewSet, basename="deactivedslot")
# router.register("mypatient", v.MyPatientViewSet, basename="mypatient")

app_name = "api"
urlpatterns = [
    # path("mypatient/", v.ListMyPatientsView.as_view()),
    path("appointment-conditionthread/", v.ListCreateAppointmentConditionTreatView.as_view()),
    path("weekdays/", v.ListWeekDaysView.as_view()),
    # path("", include(router.urls)),
]


"""
Doctor APIs
NOTE: you need to be athenticated to query in these APIS

# Doctor
endpoint "/doctor/api/doctor/<your-id>/" : update, retrieve(put, patch)

# Clinics
-LIST endpint "/doctor/api/clinic/": all clinics
-UPDATE endpoint "/doctor/api/clinic/<clinic-id>/": you must be the clinic owner to update it



"""
