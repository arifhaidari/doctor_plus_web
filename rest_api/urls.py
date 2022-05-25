from django.conf.urls import include
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_api.user_api.views import (MyTokenObtainPairView, BasicInfo, PatientTokenObtainPairView, PatientBasicInfo, 
                                     RegisterDoctorPatient, OTPVerificationView
                                     )
from rest_api.public_api.views import (
                         ListDoctorTitleView, ListDistrictView, ListCityView, BloodGroupViewSet
                    )
from rest_api.doctor_api.views import (
     ClinicScheduleBrief, BookedApptList, MyPatientList, ViewDoctorProfile, ClinicApptAPIView, 
     CareServiceAPIView, ClinicAPIView, CityDistrictAPIView, EducationSubAPIView, ExperienceAPIView, 
     BioAPIView, AwardAPIView, PatientBookedCompletedAPIView, MedicalRecordAPIView, UserPatientDetailView, 
     FeedbackAPIView, FeedBackDetailView, NotificationAPIView, NotificationDetailView, ChangePasswordAPIView, 
     ApptDetailAPIView, BasicInfoAPIView, ProfileSubmissionAPIView
)

from rest_api.patient_api.views import (
     FindDoctorDataView, SearchDoctorView, ViewDoctorProfileDetail, 
     ApptListTileView, FavoriteDoctorListView, MedicalRecordTileView, MedicalRecordDetailView, 
     MedicalReocrdShareHander, MedicalReocrdGeneralShareHander, CreateMedicalRecordDataView, 
     ViewPatientOrRelativeProfileView, RelativeTileView, DoctorApptListView, ApptDetailView, PatientProfileSettingView, 
     DistrictByCityView, RelativeRelationView, UpdateRelativeInitialDataView
     )

from rest_api.chat_api.views import ChattAPIView, ChatUser

from django.views.decorators.csrf import csrf_exempt


app_name = "rest_api"

urlpatterns = [
     # User 
     path('user/otp/', OTPVerificationView.as_view(), name='otp'),
     
     # User Doctor path
     # path('user/register/', RegisterUser.as_view(), name='register'),
     path('user/register/', RegisterDoctorPatient.as_view(), name='doctor_patient_register'),
     path('token/custom/', MyTokenObtainPairView.as_view(), name='only_token'), # only return token // for doctor
     # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('user/basic/info/', BasicInfo.as_view(), name='basic_info'),
     
     # User Patient path
     path('token/patient/', PatientTokenObtainPairView.as_view(), name='patient_token'), # only return token // for doctor
     path('patient/basic/info/', PatientBasicInfo.as_view(), name='patient_basic_info'),
     
     # Doctor
     path('doctor/clinic/brief/', ClinicScheduleBrief.as_view(), name='clinic_brief'),
     path('doctor/booked/appt/', BookedApptList.as_view(), name='booked_appt_list'),
     path('doctor/patient/list/', MyPatientList.as_view(), name='my_patient_list'),
     path('doctor/view/profile/<user>/', ViewDoctorProfile.as_view(), name='view_doctor_profile'),
     path('doctor/appt/list/', ClinicApptAPIView.as_view(), name='clinic_all_appt'),
     path('doctor/clinic/list/', ClinicAPIView.as_view(), name='clinic_list'),
     path('doctor/experience/list/', ExperienceAPIView.as_view(), name='experience_get_post'),
     path('doctor/bio/list/', BioAPIView.as_view(), name='bio_get_post'),
     path('doctor/award/list/', AwardAPIView.as_view(), name='award_get_post'),
     path('doctor/patient/detail/', PatientBookedCompletedAPIView.as_view(), name='patient_detail_view'),
     path('doctor/patient/record/', MedicalRecordAPIView.as_view(), name='patient_medical_record'),
     path('doctor/patient/<id>/', UserPatientDetailView.as_view(), name='patient_user_detail'),
     path('doctor/feedback/<id>/', FeedBackDetailView.as_view(), name='feedback_detail'),
     path('doctor/appt/feedback/', FeedbackAPIView.as_view(), name='doctor_feedback'),
     path('doctor/note/list/', NotificationAPIView.as_view(), name='notification_get'),
     path('doctor/note/<id>/', NotificationDetailView.as_view(), name='notification_delete'),
     path('doctor/change/pass/', ChangePasswordAPIView.as_view(), name='change_pass'),
     path('doctor/appt/detail/<id>/', ApptDetailAPIView.as_view(), name='doctor_appt_detail'),
     path('doctor/basic/info/<id>/', BasicInfoAPIView.as_view(), name='doctor_basic_info'),
     path('doctor/profile/submission/', ProfileSubmissionAPIView.as_view(), name='doctor_profile_submission'),
     
     # General path
     path('public/title/', ListDoctorTitleView.as_view(), name='doctor_title'),
     path('public/city/', ListCityView.as_view(), name='city'),
     path('public/district/', ListDistrictView.as_view(), name='district'),
     path('public/boold/', BloodGroupViewSet.as_view(), name='blood_group'),
     path('public/care/service/', CareServiceAPIView.as_view(), name='care_service_list'),
     path('public/city/district/list/', CityDistrictAPIView.as_view(), name='care_service_list'),
     path('public/education/sub/list/', EducationSubAPIView.as_view(), name='education_sub_list'),
     
     # chat
     path('chat/<str:username>/', ChattAPIView.as_view(), name='chat_list_post'),
     path('chat/user/list/', ChatUser.as_view(), name='user_chat_list'),
     
     # Patient
     path('patient/find-doctor/', FindDoctorDataView.as_view(), name='find_doctor'),
     path('patient/search/doctor/', SearchDoctorView.as_view(), name='find_doctor'),
     path('patient/view/doctor/profile/<user>/', ViewDoctorProfileDetail.as_view(), name='view_doctor_detail'),
     path('patient/appt/create/list/', ApptListTileView.as_view(), name='appt_create_list'),
     path('patient/favorite/create/list/', FavoriteDoctorListView.as_view(), name='favoite_doctor_create_list'),
     path('patient/medical/create/list/', MedicalRecordTileView.as_view(), name='medical_record_create_list'),
     path('patient/medical/detail/<id>/', MedicalRecordDetailView.as_view(), name='medical_record_detail'),
     path('patient/medical/share/', MedicalReocrdShareHander.as_view(), name='medical_record_share_handler'),
     path('patient/medical/general/share/', MedicalReocrdGeneralShareHander.as_view(), name='medical_record_general_share_handler'),
     path('patient/medical/create/data/', CreateMedicalRecordDataView.as_view(), name='create_medial_data'),
     path('patient/relative/profile/<id>/', ViewPatientOrRelativeProfileView.as_view(), name='patient_relative_profile'),
     path('patient/family/list/', RelativeTileView.as_view(), name='relative_tile_list'),
     path('patient/doctor/appt/<id>/<clinic_id>/', DoctorApptListView.as_view(), name='doctor_appt_list'),
     path('patient/appt/detail/<id>/', ApptDetailView.as_view(), name='appt_detail'),
     path('patient/profile/setting/', PatientProfileSettingView.as_view(), name='patient_profile_setting'),
     path('patient/district/list/', DistrictByCityView.as_view(), name='district_list_by_city'),
     path('patient/relative/list/', RelativeRelationView.as_view(), name='patient_relative_list'),
     path('patient/relative/initial/', UpdateRelativeInitialDataView.as_view(), name='update_initial_data'),
]

