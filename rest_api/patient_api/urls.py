from rest_framework.routers import DefaultRouter

from django.urls import path, include
# from .views import FindDoctorDataView
# from . import views as v

# router = DefaultRouter()
# router.register("profile", v.PatientViewSet, basename="profile")
# router.register("relative", v.RelativeViewSet, basename="relative")
# router.register("appointment", v.AppointmentViewSet, basename="appointment")
# router.register("feedback", v.FeedbackViewSet, basename="feedback")
# router.register("feedback_reply", v.FeedbackRepliesViewSet, basename="feedback_reply")
# router.register("notification", v.NotificationViewSet, basename="notification")
# router.register("medicalrecord", v.MedicalRecordsViewSet, basename="medicalrecord")
# router.register("favorite_doctor", v.FavoriteDoctorViewSet, basename="favorite_doctor")


app_name = "api-patient"
urlpatterns = [
    # path('patient/find-doctor/', FindDoctorDataView.as_view(), name='')
]

"""
# Appointments
- List
endpoint "/patient/api/appointment/" lists all appointments of the current patient
or for relative appointment use "/patient/api/appointment/?relative=<relative-id>"
SEARCH: filtering by doctor use "/patient/api/appointment/?doctor=<doctor-id>"
doctor-id = doctor.user.id
relative-id = relative.user.id
and so on..

- Add appointment(book)
to book an appointment send post request to endpoint "/patient/api/appointment/"
the post request should looks like this
{
    "doctor": 1,
    "clinic": 5,
    "relative": 6,
    // relative is optional(if it was empty it will be booked for self)
    "appt_date": "2021-05-24",
    "start_appt_time": "07:30:00",
    "end_appt_time": "08:30:00"
}

- Delete(actually it cancels the appointment here, instated of deleting the appointment)
endpoint "/patient/api/appointment/<appointment-id>/"
if it's a relative appointment then "/patient/api/appointment/<appointment-id>/?relative=<relative-id>"

- Updating the appointment(Rescheduling)
Updating an appointment is ** Not Allowed! ** for a patient if in the case of he/she want to reschedule appointment
he/she has to delete the current appointment(the delete cancels the appointment noting more) and than
book a new appointment on empty appointment slots


# Appointment Feedbacks
- List: endpoint "/patient/api/feedback/"
- Details: endpoint "/patient/api/feedback/<feedback-id>/"

* Reply
-- add: endpoint "/patient/api/feedback_reply/"
{
    "feedback": <feedback-id>,
    "reply": ""
}
-- edit: endpoint "/patient/api/feedback_reply/<reply-id>/"
{
    "reply": ""
}
-- delete: endpoint "/patient/api/feedback_reply/<reply-id>/"



# Medicalrecords
- List
endpoint "/patient/api/medicalrecord/" or "/patient/api/medicalrecord/?relative=<relative-id>"
SEARCH: if you want filter by doctor use "/patient/api/medicalrecord/?doctor=<doctor-id>"

- Add MedicalRecord
endpoint "/patient/api/medicalrecord/"
{
    "title": "",
    "relative": <relative-id> // optional
    "doctor": <doctor-id>,
    "file": <your-real-file>
}

- Edit MedicalRecord
endpoint "/patient/api/medicalrecord/<medicalrecord-id>" or
"/patient/api/medicalrecord/<medicalrecord-id>/?relative=<relative-id>"
{
    "title": "",
    "doctor": 1,
    "doctor_access": true,
    "general_access": true,
    "file": <your-file>
}

- Delete MedicalRecord
endpoint /patient/api/medicalrecord/<medicalrecord-id>
or "/patient/api/medicalrecord/<medicalrecord-id>/?relative=<relative-id>"


# Favorite Doctor
- List
endpoint "/patient/api/favorite_doctor/"

- Update
endpoint "/patient/api/favorite_doctor/<favorite-doctor-object-id>/"


# Relative
- List: endpoint "/patient/api/relative/"

- Add
endpoint "/patient/api/relative/"
{
    "user": {
        "full_name": "",
        "rtl_full_name": "",
        "avatar": <file>, // optional
        "gender": "Female",
        "phone": "",
    },
    "blood_group": <id>,
    "rel": <id>
}

- Edit: endpoint "/patient/api/relative/<relative-user-id>/"
- Delete: endpoint "/patient/api/relative/<relative-user-id>/"

# Notification ------------------------------------------

# User Profile
- Reterive: endpoint "/patient/api/user/<user-id>/"
- Update: endpoint "/patient/api/user/<user-id>/"

"""
