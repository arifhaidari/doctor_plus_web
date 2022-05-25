from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Count
from user.models import User, Doctor, Patient, Speciality  # , SpecialityCategory
from appointment.models import Appointment, Feedback  # , AppointmentConditionThread
from doctor.models import Clinic
from . import forms


# Create your views here.
class AdminplusAuthMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        if self.has_adminplus_permission(request):
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()

    def has_adminplus_permission(self, request):
        temp_bool = True if request.user.user_type == User.Types.AdminPlus else False
        return temp_bool


class AdminDashboard(AdminplusAuthMixin, generic.TemplateView):
    template_name = "adminplus/adminp_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(AdminDashboard, self).get_context_data(**kwargs)
        doctor_queryset = Doctor.objects.all()
        patients = Patient.objects.all().count()
        data = {
            "doctor_count": doctor_queryset.filter(professional_status=True).count(),
            "doctors_under_review_count": doctor_queryset.filter(professional_status=False, is_profile_on_progress=True).count(),
            "patient_count": patients,
            "appointment_count": Appointment.objects.filter(status=Appointment.ApptStatus.COMPLETED).count(),
        }
        context.update(data)
        return context


# class Appointments(AdminplusAuthMixin, generic.ListView):
#     model = Appointment
#     template_name = "adminplus/pages/appointment/appointment.html"
#     get_queryset = lambda self: Appointment.objects.filter(patient__isnull=False)


# class ConditionThreadListView(AdminplusAuthMixin, generic.ListView):
#     model = Appointment
#     template_name = "adminplus/pages/appointment/condition_threads.html"

#     def get_queryset(self):
#         return Appointment.objects.filter(
#             patient__isnull=False,
#             condition_threaded__isnull=False,
#             status=Appointment.ApptStatus.COMPLETED,
#         )

#     def get_context_data(self, **kwargs):
#         context = super(ConditionThreadListView, self).get_context_data(**kwargs)
#         appointments = self.object_list.values(
#             "condition_threaded__id",
#             "condition_threaded__name",
#             "clinic__city__name",
#         ).annotate(Count("condition_threaded"))
#         context["report_apps"] = appointments

#         print("appointments : ", appointments)
#         return context


# class Specialities(AdminplusAuthMixin, generic.ListView):
#     model = Speciality
#     template_name = "adminplus/pages/speciality/specialities.html"

#     def get_context_data(self, **kwargs):
#         context = super(Specialities, self).get_context_data(**kwargs)
#         data = {"add_speciality_form": forms.SpecialityForm()}
#         context.update(data)
#         return context

#     def post(self, request, *args, **kwargs):
#         # add new speciality
#         if request.POST.get("new_speciality"):
#             speciality = forms.SpecialityForm(request.POST, request.FILES)
#             if speciality.is_valid():
#                 speciality.save()
#                 data = {"add_status": "success"}
#                 return JsonResponse(data)
#         # delete speciality
#         elif request.POST.get("delete_speciality"):
#             get_object_or_404(Speciality, id=request.POST.get("delete_id")).delete()
#             return JsonResponse({"delete": "success"})


# class SpecialityUpdateView(AdminplusAuthMixin, generic.UpdateView):
#     model = Speciality
#     success_url = "."
#     form_class = forms.SpecialityForm
#     template_name = "adminplus/pages/speciality/edit_speciality.html"

#     def get_context_data(self, **kwargs):
#         context = super(SpecialityUpdateView, self).get_context_data(**kwargs)
#         condition_form = forms.condition_formset(instance=self.object)
#         service_form = forms.service_formset(instance=self.object)
#         context["condition_form"] = condition_form
#         context["service_form"] = service_form
#         return context

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if request.POST.get("conditions"):
#             condition_form = forms.condition_formset(request.POST, instance=self.object)
#             condition_form.is_valid() and condition_form.save()
#         if request.POST.get("services"):
#             print("detected service form!")
#             service_form = forms.service_formset(request.POST, instance=self.object)
#             service_form.is_valid() and service_form.save()
#         if request.POST.get("speciality"):
#             return super(SpecialityUpdateView, self).post(request, **kwargs)
#         return JsonResponse({"status": "success"})


class DoctorListView(AdminplusAuthMixin, generic.ListView):
    context_object_name = "doctors"
    template_name = "adminplus/pages/doctor/doctors.html"
    queryset = Doctor.objects.filter(professional_status=True)

    def post(self, request, *args, **kwargs):
        if request.POST.get("active_doctor"):
            doctor = get_object_or_404(Doctor, user__id=request.POST.get("active_doctor"))
            doctor.user.suspend = False
            doctor.user.save()
        elif request.POST.get("deactive_doctor"):
            doctor = get_object_or_404(Doctor, user__id=request.POST.get("deactive_doctor"))
            doctor.user.suspend = True
            doctor.user.save()
            # kicking out if user is login
            for s in Session.objects.all():
                data = s.get_decoded()
                if data.get("_auth_user_id", None) == str(doctor.user.id):
                    s.delete()
        if request.POST.get("delete_doctor"):
            doctor = get_object_or_404(Doctor, user__id=request.POST.get("delete_doctor"))
            # doctor.user.delete()
            print("doctor with user id : ", doctor.user.id, " deleted!")
        return JsonResponse({"status": "success"})


class DoctorDetailView(AdminplusAuthMixin, generic.DetailView):
    model = Doctor
    context_object_name = "doctor"
    template_name = "adminplus/pages/doctor/doctor_profile.html"

    def get_context_data(self, **kwargs):
        context = super(DoctorDetailView, self).get_context_data(**kwargs)
        # data = {"edit_form": forms.DoctorEditForm(instance=self.object)}
        # context.update(data)
        return context

    def post(self, request, *args, **kwargs):
        doctor = self.get_object()
        active_doctor = request.POST.get("active_doctor")
        if active_doctor:
            suspend_status = False if active_doctor == "1" else True
            doctor.user.suspend = suspend_status
            doctor.user.save()
            # kicking out if user is login
            for s in Session.objects.all():
                data = s.get_decoded()
                if data.get("_auth_user_id", None) == str(doctor.user.id):
                    s.delete()
            return JsonResponse({"status": "success"})
        if request.POST.get("delete_doctor"):
            # doctor.user.delete()
            return JsonResponse({"status": "success"})


class DoctorReviewRequest(AdminplusAuthMixin, generic.TemplateView):
    template_name = "adminplus/pages/doctor/review_requests.html"

    def get_context_data(self, **kwargs):
        context = super(DoctorReviewRequest, self).get_context_data(**kwargs)
        context["review_requests"] = Doctor.objects.filter(is_profile_on_progress=True)
        return context

    def post(self, request, *args, **kwargs):
        # approve doctor
        if request.POST.get("approve"):
            doctor = get_object_or_404(Doctor, user__id=request.POST.get("approve"))
            doctor.professional_status = True  # 2 stands for active
            doctor.save()
            return JsonResponse({"status": "success", "id": request.POST.get("approve")})
        # reject
        elif request.POST.get("reject"):
            doctor = get_object_or_404(Doctor, user__id=request.POST.get("reject"))
            doctor.is_profile_on_progress = False  # 0 stands for None
            doctor.professional_status = False  # 0 stands for None
            doctor.save()
            # sending the rejection notification to doctor
            # reason = request.POST.get("reason")
            # review_notifications.review_request_rejected(doctor=doctor, reason=reason)
            return JsonResponse({"status": "success", "id": request.POST.get("reject")})


class PatientListView(AdminplusAuthMixin, generic.ListView):
    model = Patient
    context_object_name = "patients"
    template_name = "adminplus/pages/patient/patients.html"

    def post(self, request, *args, **kwargs):
        print("patient post : ", request.POST)
        if request.POST.get("active_patient"):
            patient = get_object_or_404(Patient, user__id=request.POST.get("active_patient"))
            patient.user.suspend = False
            patient.user.save()
        elif request.POST.get("deactive_patient"):
            patient = get_object_or_404(Patient, user__id=request.POST.get("deactive_patient"))
            patient.user.suspend = True
            patient.user.save()
            # kicking out if user is login
            for s in Session.objects.all():
                data = s.get_decoded()
                if data.get("_auth_user_id", None) == str(patient.user.id):
                    s.delete()
        if request.POST.get("delete_patient"):
            patient = get_object_or_404(Patient, user__id=request.POST.get("delete_patient"))
            # patient.user.delete()
            print("patient with user id : ", patient.user.id, " deleted!")
        return JsonResponse({"status": "success"})


class PatientDetailView(AdminplusAuthMixin, generic.DetailView):
    model = Patient
    context_object_name = "patient"
    template_name = "adminplus/pages/patient/patient_profile.html"

    def get_context_data(self, **kwargs):
        context = super(PatientDetailView, self).get_context_data(**kwargs)
        context["completed_apps"] = Appointment.objects.filter(
            patient=self.object, relative__isnull=False, status=Appointment.ApptStatus.COMPLETED
        )
        return context

    def post(self, request, *args, **kwargs):
        patient = self.get_object()
        active_patient = request.POST.get("active_patient")
        if active_patient:
            suspend_status = False if active_patient == "1" else True
            print("suspend_status : ", suspend_status, " the active_patient : ", active_patient)
            patient.user.suspend = suspend_status
            patient.user.save()
            # kicking out if user is login
            for s in Session.objects.all():
                data = s.get_decoded()
                if data.get("_auth_user_id", None) == str(patient.user.id):
                    s.delete()
            return JsonResponse({"status": "success"})
        if request.POST.get("delete_patient"):
            # patient.user.delete()
            return JsonResponse({"status": "success"})


class AdminProfile(AdminplusAuthMixin, generic.TemplateView):
    model = Doctor
    template_name = "adminplus/pages/admin_profile.html"

    def get_context_data(self, **kwargs):
        context = super(AdminProfile, self).get_context_data(**kwargs)
        context["form"] = forms.AdminEditForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form = forms.AdminEditForm(request.POST, request.FILES or None, instance=request.user)
        if form.is_valid():
            form.save()

        context = super(AdminProfile, self).get_context_data(**kwargs)
        context["form"] = form
        return render(request, self.template_name, context=context)


class PasswordChangeView(AdminplusAuthMixin, PasswordChangeView):
    success_url = "."
    form_class = forms.UserPasswordChangeForm
    template_name = "adminplus/components/change_password.html"


class ClinicListView(AdminplusAuthMixin, generic.ListView):
    model = Clinic
    template_name = "adminplus/pages/clinic/clinics.html"

    def post(self, request, *args, **kwargs):
        if request.POST.get("suspend-clinic"):
            clinic = get_object_or_404(Clinic, id=request.POST.get("suspend-clinic"))
            clinic.active = True if request.POST.get("active") == "true" else False
            clinic.save()
        elif request.POST.get("delete_clinic"):
            # get_object_or_404(Clinic, id=request.POST.get("delete_clinic")).delete()
            print("clincic deleted!")
        return JsonResponse({})


class ClinicReviewRequests(AdminplusAuthMixin, generic.TemplateView):
    template_name = "adminplus/pages/clinic/review_requests.html"

    def get_context_data(self, **kwargs):
        context = super(ClinicReviewRequests, self).get_context_data(**kwargs)
        context["clinics"] = Clinic.objects.filter(active=False)
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("approve_clinic"):
            Clinic.objects.filter(id=request.POST["approve_clinic"]).update(active=True)
            return JsonResponse({"status": "success"})
        if request.POST.get("reject_clinic"):
            # get_object_or_404(Clinic, id=request.POST.get("reject_clinic")).delete()
            return JsonResponse({"status": "success"})
