from django.urls import path
from . import views

app_name = "medicalrecord"
urlpatterns = [
    # path("filesharing/", views.file_sharing_view, name="FileSharingView"),
    path("medical/detail/<int:pk>/", views.MeicalRecordDetail.as_view(), name="medical_detail"),
    path("medical/add/", views.AddMedicalRecord.as_view(), name="add_medical"),
    path("medical/edit/<id>/", views.EditMedicalRecord.as_view(), name="edit_medical"),
]
