from django.urls import path

from . import views


app_name = "relative"
urlpatterns = [
    path("", views.RelativeList.as_view(), name="list"),
    path("detail/<pk>/", views.RelativeDetail.as_view(), name="detail"),
    path("appt/detail/<pk>/", views.ApptDetail.as_view(), name="appt_detail"),
]
