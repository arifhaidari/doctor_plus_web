from django.urls import path, include

# from chat.models import Chat
from .views import (
    PatientPassword,
    FavoriteDoctorListView,
    PatientProfileSetting,
    save_patient_avatar,
    patient_review_view,
    patient_dashboard_view,
    PatientNotification,
    FeedbackHandler
)

app_name = "patient"
urlpatterns = [
    path("", patient_dashboard_view, name="patient_dashboard_view"),
    path("password/", PatientPassword.as_view(), name="change_password"),
    path("favorite/", FavoriteDoctorListView.as_view(), name="favorite_doctor"),
    path("notifications/", PatientNotification.as_view(), name="notifications"),
    path("profile/", PatientProfileSetting.as_view(), name="patient_profile"),
    path("feedback/<id>/", FeedbackHandler.as_view(), name="feedback"),
    path("avatar/", save_patient_avatar, name="save_patient_avatar"),
    path("review/<str:appointment>/", patient_review_view, name="patient_review_view"),
    # api
    path("api/", include("rest_api.patient_api.urls")),
]
