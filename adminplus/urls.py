from django.urls import path
from . import graphs
from . import views


app_name = "adminplus"
urlpatterns = [
    path("", views.AdminDashboard.as_view(), name="dashboard"),
    # appointment
    # path("appointments/", views.Appointments.as_view(), name="appointments"),
    # path("conditionthreads/", views.ConditionThreadListView.as_view(), name="condition_threads"),
    # specialities, conditions, services
    # path("specialities/", views.Specialities.as_view(), name="specialities"),
    # path("edit_speciality/<pk>/", views.SpecialityUpdateView.as_view(), name="edit_speciality"),
    # doctor
    path("doctors/", views.DoctorListView.as_view(), name="doctors"),
    path("doctorprofile/<pk>/", views.DoctorDetailView.as_view(), name="doctor_profile"),
    path("doctor_reviews/", views.DoctorReviewRequest.as_view(), name="doctor_reviews"),
    # patient
    path("patients/", views.PatientListView.as_view(), name="patients"),
    path("patientprofile/<pk>/", views.PatientDetailView.as_view(), name="patient_profile"),
    # clinics
    path("clinics/", views.ClinicListView.as_view(), name="clinics"),
    path("clinic_reviews/", views.ClinicReviewRequests.as_view(), name="clinic_reviews"),
    # adminplus admin
    path("adminprofile/", views.AdminProfile.as_view(), name="adminprofile"),
    path("passwordchange/", views.PasswordChangeView.as_view(), name="password_change"),
    # data
    path("dashboard-graphs/", graphs.dashboard_graph, name="dashboard_graphs"),
]

