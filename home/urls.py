from django.urls import path

# from .views import Home, DoctorPublicProfile
from . import views

app_name = "home"
urlpatterns = [
    # path("", views.Home.as_view(), name="homepage"),
    path("", views.home_view, name="homepage"),
    path("search/", views.search_view, name="search_view"),
    path("public/doctor/<pk>/", views.DoctorProfileDetailView.as_view(), name="doctor_public_profile"),
]
