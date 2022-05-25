from django.urls import path, include
from .views import (
    LoginView,
    PatientRegisterView,
    user_verify,
    DoctorRegisterView,
    load_districts,
    SocialAuthUserAdapter,
)

app_name = "user"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("patient/register/", PatientRegisterView.as_view(), name="patient_register"),
    path("doctor/register/", DoctorRegisterView.as_view(), name="doctor_register"),
    path("user/verify/<dict>/", user_verify, name="verify_user"),
    path("ajax/districts/", load_districts, name="ajax_load_districts"),
    path("socialadp/", SocialAuthUserAdapter.as_view(), name="social_adp"),
    # added api path
    # path("api/", include("rest_api.user_api.urls", namespace="account-api")),
]
