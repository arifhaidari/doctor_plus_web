# from django.urls import path, include


# from rest_framework_simplejwt import views as jwt_views
# from rest_framework.routers import DefaultRouter

# from . import views as v


# router = DefaultRouter()
# # router.register("auth/registration", v.RegisterUser, basename="cuser")
# # 
# router.register("blood", v.BloodGroupViewSet, basename="blood")
# router.register("relationship", v.RelativeRelationshipsViewSet, basename="relationship")
# router.register("search", v.SearchVieSet, basename="search")
# router.register("blog", v.PostViewSet, basename="blog")

# app_name = "user-api"
# urlpatterns = [
#     # # my edited api
#     # path('auth/registration/', v.RegisterUser.as_view(), name='register'),
#     # //
#     path("token/", jwt_views.TokenObtainPairView.as_view(), name="get_token"),
#     path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="refresh_token"),
#     # path("logout/", v.LogoutView.as_view()),
#     path("auth/", include("dj_rest_auth.urls")),
#     # path("auth/registration/", include("dj_rest_auth.registration.urls")),
#     path("auth/facebook/", v.FacebookLogin.as_view(), name="fb_login"),
#     # general paths
#     path("", include(router.urls)),
#     path("doctor-title/", v.ListDoctorTitleView.as_view()),
#     path("cities/", v.ListCityView.as_view()),
#     path("districts/", v.ListDistrictView.as_view()),
#     # path("search/", v.ListSearchView.as_view(), name="search"),
# ]



# DOCOR API

# from django.urls import path
# from rest_framework.routers import DefaultRouter

# from . import views as v

# from django.urls import include

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
# router.register("daypattren", v.DaySchedulePatternViewSet, basename="day")
# router.register("deactivedslot", v.DeactivatedApptSlotViewSet, basename="deactivedslot")
# router.register("mypatient", v.MyPatientViewSet, basename="mypatient")

# app_name = "api"
# urlpatterns = [
#     # path("mypatient/", v.ListMyPatientsView.as_view()),
#     path("appointment-conditionthread/", v.ListCreateAppointmentConditionThreadView.as_view()),
#     path("weekdays/", v.ListWeekDaysView.as_view()),
#     path("", include(router.urls)),
# ]


# """
# Doctor APIs
# NOTE: you need to be athenticated to query in these APIS

# # Doctor
# endpoint "/doctor/api/doctor/<your-id>/" : update, retrieve(put, patch)

# # Clinics
# -LIST endpint "/doctor/api/clinic/": all clinics
# -UPDATE endpoint "/doctor/api/clinic/<clinic-id>/": you must be the clinic owner to update it



# """
