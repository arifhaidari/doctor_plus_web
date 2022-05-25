from django.urls import path, include
from . import views
from .views import (
    DoctorNotification,
    DoctorChangePassword,
    DoctorProfile,
    SocialMediaProfile,
    AddPrescription,
    load_services,
    load_conditions,
    load_json_districts,
    get_json_city,
    add_appointment_condition_thread,
    load_degree_names,
    load_degrees
)

app_name = "doctor"

urlpatterns = [
    path("", views.doctor_dashboard_view, name="dashboard"),
    path("ajax/conditions/", load_conditions, name="ajax_load_conditions"),
    path("ajax/services/", load_services, name="ajax_load_services"),
    path("json/degree/", load_degrees, name="load_degrees"),
    path("json/degree/names/", load_degree_names, name="load_degree_names"),
    path("json/city/", get_json_city, name="get_json_city"),
    path("json/district/", load_json_districts, name="load_json_city"),
    path("note/", DoctorNotification.as_view(), name="doctor_note"),
    path("password/", DoctorChangePassword.as_view(), name="doctor_password"),
    path("patient/", views.doctor_mypatients_view, name="my_patient"),
    path("patient/detail/<str:type>/<int:id>/", views.doctor_mypatient_detail_view, name="my_patient_detail"),
    path("prescription/", AddPrescription.as_view(), name="prescription"),
    path("profile/", DoctorProfile.as_view(), name="doctor_profile"),
    path("review/", views.doctor_review_view, name="doctor_review"),
    path("review/<pk>/", views.ReviewDetailView.as_view(), name="doctor_specific_review"),
    path("socialmedia/", SocialMediaProfile.as_view(), name="socialmedia"),
    path("addappthread/", add_appointment_condition_thread, name="add_app_condtition_thread"),
    # api
    # path("api/", include("rest_api.doctor_api.urls", namespace="api")),
]
