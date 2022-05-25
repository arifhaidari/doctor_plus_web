from ast import operator
from DoctorPlus.utils import calculate_patient_appt
from notification.notification_manager import appt_canceled_by_doctor, review_relplied_by_doctor
from . import forms
from notification.models import Notification
# from notification import review_notifications as notifications_manager
from appointment.models import Appointment, Feedback, ApptConditionTreat, ApptQrCode, FeedbackReplies
from chat.models import ChatMessage as Chat
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Q, fields
from django.db.models.aggregates import Count
from django.db.models.expressions import F
from django.http import JsonResponse, Http404
from django.http.response import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, View, FormView
from doctor.models import Award, Clinic, DegreeType, Education, EducationDegree, Experience
from home.models import DoctorSocialMedia, City, District, Address
from patient.views import save_user_address
import datetime
from .forms import SocialMediaForm, ApptConditionTreatForm
from user.models import (
    Condition,
    Doctor,
    DoctorTitle,
    Patient,
    Relative,
    BloodGroup,
    Service,
    Speciality,
)
from medicalrecord.models import MedicalRecords

# from appointment.models import Feedback
# from django.db.models import Count

User = get_user_model()


# def is_authorized_doctor(view):
#     def wrapper():
#         if request.user.user_type == request.user.user_type == "DOCTOR":
#             view()
#         print("Something is happening after the function is called.")

#     return wrapper


is_post_request = lambda request: request.method == "POST"
is_user_auhenticated = lambda request: request.user.is_authenticated and request.user.user_type == "Doctor"


def doctor_dashboard_view(request, *args, **kwargs):
    if not is_user_auhenticated(request):
        return HttpResponseForbidden()
    appoinments = Appointment.objects.filter(patient__isnull=False, doctor=request.user.doctor)
    today_appoinments = appoinments.filter(appt_date=datetime.datetime.today().date())
    tomorrow_appoinments = appoinments.filter(appt_date=datetime.date.today() + datetime.timedelta(days=1))
    upcoming_appoinments = appoinments.filter(appt_date__range=(datetime.date.today() + datetime.timedelta(days=2), datetime.date.today() + datetime.timedelta(days=15)))
    # completed_appts = appoinments.filter(status=Appointment.ApptStatus.COMPLETED).count()
    completed_appt_no, patient_no = calculate_patient_appt(request.user.doctor)
    total_patients_today = appoinments.filter(appt_date=datetime.datetime.today().date()).count()

    # while doctor cancels the appoinment
    if request.POST.get("cancel_appointment"):
        appoint = get_object_or_404(Appointment, id=request.POST.get("cancel_appointment"))
        # sending the cancel notification to patient
        appt_canceled_by_doctor(appoint)
        # canceling the appointment
        appoint.status, appoint.patient, appoint.relative = "PENDING", None, None
        appoint.save()
        # deleting the Qr Code of appointment
        ApptQrCode.objects.filter(appt_slot=appoint).delete()

        return JsonResponse({"status": "success", "id": appoint.id})
    if request.POST.get("appid"):
        appointment = Appointment.objects.get(id=request.POST.get("appid"))
        if request.POST.get("condition_threads"):
            appointment.condition_threaded.clear()
            for x in request.POST.getlist("condition_threads"):
                appointment.condition_threaded.add(x)
        elif request.POST.get("app_conditions"):
            return JsonResponse({"conditions": [x.id for x in appointment.condition_threaded.all()]})

    context = {
        "appointments": appoinments,
        "today_appoinments": today_appoinments,
        "tomorrow_appoinments": tomorrow_appoinments,
        "upcoming_appoinments": upcoming_appoinments,
        "completed_appt_no": completed_appt_no,
        "patient_no": patient_no,
        "total_patients_today": total_patients_today,
        "add_app_codition_thread": ApptConditionTreatForm(),
        "appt_condition_treated": ApptConditionTreat.objects.all(),
    }
    return render(request, "doctor/doctor_dashboard.html", context)


def doctor_mypatients_view(request, *args, **kwargs):
    if not is_user_auhenticated(request):
        return HttpResponseForbidden()
    my_patients = Appointment.objects.filter(status=Appointment.ApptStatus.COMPLETED, doctor=request.user.doctor).order_by(
        "patient"
    )
    # my_patients = Appointment.objects.filter(status=Appointment.ApptStatus.COMPLETED, doctor=request.user.doctor)
    patients = my_patients.filter(relative__isnull=True)
    relatives = my_patients.filter(relative__isnull=False)

    context = {
        "my_patients": my_patients,
        "patients": patients,
        "patient_relatives": relatives,
    }
    return render(request, "doctor/my_patient.html", context)


def doctor_mypatient_detail_view(request, *args, **kwargs):
    if not is_user_auhenticated(request):
        return HttpResponseForbidden()
    # relative
    if kwargs.get("type") == "rel":
        # medicalrecord related
        patient = get_object_or_404(Relative, user__id=kwargs["id"])
        medical_filter = Q()
        if not patient.share_record_to_all:
            medical_filter.add(Q(Q(general_access = True) | Q(related_doctor = request.user.doctor)), Q.AND)
        medicalrecords = MedicalRecords.objects.filter(relative=patient).filter(medical_filter).order_by('-timestamp')
        # appointment related
        appointments = Appointment.objects.filter(relative=patient, doctor=request.user.doctor).order_by('-appt_date')
        print("is relative true : ", patient)
    # patient
    else:
        # medicalrecord related
        patient = get_object_or_404(Patient, user__id=kwargs["id"])
        medical_filter = Q()
        if not patient.share_record_to_all:
            medical_filter.add(Q(Q(general_access = True) | Q(related_doctor = request.user.doctor)), Q.AND)
        medicalrecords = MedicalRecords.objects.filter(patient=patient, relative=None)
        # appointment related
        appointments = Appointment.objects.filter(patient=patient, relative=None, doctor=request.user.doctor).order_by('-appt_date')

    if request.method == "POST":
        appointment = Appointment.objects.get(id=request.POST.get("appid"))
        if request.POST.get("condition_treated"):
            appointment.condition_treated.clear()
            for condition_id in request.POST.getlist("condition_treated"):
                condition_object = ApptConditionTreat.objects.get(id=condition_id)
                appointment.condition_treated.add(condition_object)
        elif request.POST.get("app_conditions"):
            return JsonResponse({"conditions": [x.id for x in appointment.condition_treated.all()]})

    # medicalrecords = MedicalRecords.objects.filter(patient=filesharing_patient)
    context = {
        "patient": patient,
        "medicalrecords": medicalrecords,
        "appointments": appointments,
        "add_app_codition_thread": ApptConditionTreatForm(),
        "appt_condition_treated": ApptConditionTreat.objects.all(),
    }
    return render(request, "doctor/my_patient_detail.html", context)


class AddPrescription(ListView):
    template_name = "doctor/add_prescription.html"
    model = Patient


class DoctorNotification(ListView):
    model = Notification
    context_object_name = "notifications"
    template_name = "doctor/doctor_notification.html"
    get_queryset = lambda self: Notification.objects.filter(receiver=self.request.user).order_by("-timestamp")

    def post(self, request, *args, **kwargs):
        if request.POST.get('clear_notification'):
            print('insde the clear all of ntoe')
            Notification.objects.filter(receiver=self.request.user).delete()
            return JsonResponse({'status': 'success'})

        return render(request, self.template_name, {})


class DoctorChat(ListView):
    template_name = "doctor/doctor_chat.html"
    model = Chat


def professional_profile(professional_dict, doctor):
    try:
        formated_dict = dict(professional_dict)
        if professional_dict.get("specialist"):
            doctor.speciality.clear()
            for special in formated_dict['specialist']:
                special_object = Speciality.objects.get(id=special)
                doctor.speciality.add(special_object)
        if professional_dict.get("services"):
            doctor.service.clear()
            for service in formated_dict['services']:
                print(service)
                service_object = Service.objects.get(id=service)
                doctor.service.add(service_object)
        if professional_dict.get("conditions"):
            doctor.condition.clear()
            for condition in formated_dict['conditions']:
                print(condition)
                condition_object = Condition.objects.get(id=condition)
                doctor.condition.add(condition_object)
    except Exception as e:
        print('value of errror in professinal profile')


def save_clinic(clinic_dict, doctor, request):
    print("//////////Clinic")
    print('valeu of clinic_dict')
    print(clinic_dict)
    try:
    # when registered_clinics is empty it shows error then I should handle it 
        is_registered_clinics = False
        try:
            existing_clinics = clinic_dict["registered_clinics"]
            is_registered_clinics = True
        except:
            pass
        if is_registered_clinics:
            if clinic_dict["registered_clinics"]:
                previous_clinics = Clinic.objects.filter(doctor=doctor).exclude(created_by=doctor)
                for previous_obj in previous_clinics:
                    previous_obj.doctor.remove(doctor)
                for clinic_id in clinic_dict.get("registered_clinics"):
                    clinic_object = Clinic.objects.get(id=clinic_id)
                    clinic_object.doctor.add(doctor)
        input_length = 0
        if clinic_dict.get("clinic_name"):
            input_length = len(clinic_dict.get("clinic_name"))
        clinic_existing_object = Clinic.objects.filter(doctor=doctor)
        clinic_edited_object = clinic_dict.get("clinic_id_list")
        is_four_clinic = False
        is_clinic_exist = False
        if clinic_existing_object:
            # show_error_message = False
            # print("inside the clinic_existing_object and not clinic_edited_object:")
            # my_clinics = Clinic.objects.filter(created_by=doctor)
            # for this_doctor_clinic in my_clinics:
            #     doctor_clinic_length = this_doctor_clinic.doctor.count()
            #     if clinic_edited_object:
            #         if str(this_doctor_clinic.id) not in clinic_edited_object:
            #             if doctor_clinic_length > 1:
            #                 show_error_message = True
            #             else:
            #                 this_doctor_clinic.delete()
            #     else:
            #         if doctor_clinic_length > 1:
            #             show_error_message = True
            #         else:
            #             this_doctor_clinic.delete()
            # if show_error_message:
            #     messages.error(
            #         request,
            #         "You cannot delete your registered clinics because other doctors registered themselves to these clinics as well",
            #     )
            for index in range(input_length):
                is_clinic = Clinic.objects.filter(
                    Q(clinic_name__iexact=clinic_dict.get("clinic_name")[index])
                    | Q(rtl_clinic_name=clinic_dict.get("rtl_clinic_name")[index])
                )
                if is_clinic.exists():
                    try:
                        if clinic_edited_object[index]:
                            pass
                    except IndexError:
                        is_clinic_exist = True
                if is_clinic_exist:
                    clinic_object = is_clinic.first()
                    messages.error(
                        request,
                        "{} is already existed. Please select it instead of adding a new one".format(
                            clinic_object.clinic_name or clinic_object.rtl_clinic_name
                        ),
                    )
                else:
                    try:
                        if clinic_edited_object[index] and clinic_existing_object:
                            raw_existing_object = Clinic.objects.filter(id=clinic_edited_object[index])
                            if raw_existing_object:
                                city_obj = City.objects.get(id=clinic_dict.get("clinic_city")[index])
                                district_obj = District.objects.get(id=clinic_dict.get("clinic_district")[index])
                                existing_object = raw_existing_object.first()
                                existing_object.clinic_name = clinic_dict.get("clinic_name")[index]
                                existing_object.rtl_clinic_name = clinic_dict.get("rtl_clinic_name")[index]
                                existing_object.address = clinic_dict.get("clinic_address")[index]
                                existing_object.rtl_address = clinic_dict.get("rtl_clinic_address")[index]
                                existing_object.city = city_obj
                                existing_object.district = district_obj
                                existing_object.save()
                    except IndexError:
                        created_clinic_no = Clinic.objects.filter(created_by=doctor)
                        if created_clinic_no:
                            if len(created_clinic_no) <= 4:
                                create_new_clinic(clinic_dict, doctor, index)
                            else:
                                is_four_clinic = True
                        else:
                            create_new_clinic(clinic_dict, doctor, index)
            if is_four_clinic:
                messages.error(request, "You are not allowed to create more than 4 clinics")
        else:
            for index in range(input_length):
                create_new_clinic(clinic_dict, doctor, index)
    except Exception as e:
        print('value of error in save clinic')
        print(e)


def create_new_clinic(clinic_dict, doctor, index):
    print("inside the create_new_clinic")
    new_clinic_object = Clinic.objects.create(
        clinic_name=clinic_dict.get("clinic_name")[index],
        rtl_clinic_name=clinic_dict.get("rtl_clinic_name")[index],
        address=clinic_dict.get("clinic_address")[index],
        rtl_address=clinic_dict.get("rtl_clinic_address")[index],
        city=City.objects.get(id=clinic_dict.get("clinic_city")[index]),
        district=District.objects.get(id=clinic_dict.get("clinic_district")[index]),
        created_by=doctor,
    )
    
    new_clinic_object.doctor.add(doctor)


def save_education(education_dict, doctor, request):
    print("//////////Education")
    education_existing_object = Education.objects.filter(doctor=doctor)
    input_length = 0
    if education_dict.get("school_name"):
        input_length = len(education_dict.get("school_name"))
    education_edited_object = education_dict.get("education_id_list")
    is_education_exist = False
    if education_existing_object:
        my_educations = Education.objects.filter(doctor=doctor)
        for this_doctor_education in my_educations:
            if education_edited_object:
                if str(this_doctor_education.id) not in education_edited_object:
                    this_doctor_education.delete()
            else:
                this_doctor_education.delete()
        for index in range(input_length):
            is_education = Education.objects.filter(
                Q(school_name__iexact=education_dict.get("school_name")[index])
                | Q(rtl_school_name=education_dict.get("rtl_school_name")[index])
                & Q(degree__degree_type__id=education_dict.get("degree")[index])
                & Q(degree__id=education_dict.get("degree_name")[index])
            )
            if is_education.exists():
                # 351_tackle
                try:
                    if education_edited_object[index]:
                        pass
                except IndexError:
                    is_education_exist = True
            if is_education_exist:
                education_object = is_education.first()
                messages.error(
                    request,
                    "{} is already existed in your list of education.".format(education_object.degree or education_object.rtl_degree),
                )
            else:
                try:
                    if education_edited_object[index] and education_existing_object:
                        raw_existing_object = Education.objects.filter(id=education_edited_object[index])
                        if raw_existing_object:
                            existing_object = raw_existing_object.first()
                            existing_object.school_name = education_dict.get("school_name")[index]
                            existing_object.rtl_school_name = education_dict.get("rtl_school_name")[index]
                            existing_object.degree = EducationDegree.objects.get(id=education_dict.get("degree_name")[index])
                            existing_object.start_date = education_dict.get("school_start_date")[index]
                            existing_object.end_date = education_dict.get("school_end_date")[index]
                            existing_object.save()
                except IndexError:
                    create_new_education(education_dict, doctor, index)
    else:
        for index in range(input_length):
            create_new_education(education_dict, doctor, index)


def create_new_education(education_dict, doctor, index):
    Education.objects.create(
        doctor=doctor,
        school_name=education_dict.get("school_name")[index],
        rtl_school_name=education_dict.get("rtl_school_name")[index],
        degree=EducationDegree.objects.get(id=education_dict.get("degree_name")[index]),
        start_date=education_dict.get("school_start_date")[index],
        end_date=education_dict.get("school_end_date")[index],
    )


def save_experience(experience_dict, doctor, request):
    print("inside the save_experience//////====")
    print(experience_dict)
    try:
        experience_existing_object = Experience.objects.filter(doctor=doctor)
        input_length = 0
        if experience_dict.get("hospital_name"):
            input_length = len(experience_dict.get("hospital_name"))
        experience_edited_object = experience_dict.get("experience_id_list")
        if experience_existing_object:
            my_experiences = Experience.objects.filter(doctor=doctor)
            for this_doctor_experience in my_experiences:
                if experience_edited_object:
                    if str(this_doctor_experience.id) not in experience_edited_object:
                        this_doctor_experience.delete()
                else:
                    this_doctor_experience.delete()
            for index in range(input_length):
                try:
                    if experience_edited_object[index] and experience_existing_object:
                        raw_existing_object = Experience.objects.filter(id=experience_edited_object[index])
                        if raw_existing_object:
                            existing_object = raw_existing_object.first()
                            existing_object.hospital_name = experience_dict.get("hospital_name")[index]
                            existing_object.rtl_hospital_name = experience_dict.get("rtl_hospital_name")[index]
                            existing_object.designation = experience_dict.get("designation")[index]
                            existing_object.rtl_designation = experience_dict.get("rtl_designation")[index]
                            existing_object.start_date = experience_dict.get("experience_start_date")[index]
                            existing_object.end_date = experience_dict.get("experience_end_date")[index]
                            existing_object.save()
                except IndexError:
                    create_new_experience(experience_dict, doctor, index)
        else:
            for index in range(input_length):
                create_new_experience(experience_dict, doctor, index)
    except Exception as e:
        print('value fo error in save experinece')
        print(e)


def create_new_experience(education_dict, doctor, index):
    Experience.objects.create(
        doctor=doctor,
        hospital_name=education_dict.get("hospital_name")[index],
        rtl_hospital_name=education_dict.get("rtl_hospital_name")[index],
        designation=education_dict.get("designation")[index],
        rtl_designation=education_dict.get("rtl_designation")[index],
        start_date=education_dict.get("experience_start_date")[index],
        end_date=education_dict.get("experience_end_date")[index],
    )


def save_award(award_dict, doctor, request):
    print("inside the save_award")
    try:
        award_existing_object = Award.objects.filter(doctor=doctor)
        input_length = 0
        if award_dict.get("award"):
            input_length = len(award_dict.get("award"))
        award_edited_object = award_dict.get("award_id_list")
        is_award_exist = False
        if award_existing_object:
            my_awards = Award.objects.filter(doctor=doctor)
            for this_doctor_award in my_awards:
                if award_edited_object:
                    if str(this_doctor_award.id) not in award_edited_object:
                        this_doctor_award.delete()
                else:
                    this_doctor_award.delete()
            for index in range(input_length):
                is_award = Award.objects.filter(
                    Q(award_name__iexact=award_dict.get("award")[index]) | Q(rtl_award_name=award_dict.get("rtl_award")[index])
                ).filter(Q(award_year=award_dict.get("award_year")[index]))
                if is_award.exists():
                    try:
                        if award_edited_object[index]:
                            pass
                    except IndexError:
                        is_award_exist = True
                if is_award_exist:
                    award_object = is_award.first()
                    messages.error(
                        request,
                        "{} is already existed.".format(award_object.award_name or award_object.rtl_award_name),
                    )
                else:
                    try:
                        if award_edited_object[index] and award_existing_object:
                            raw_existing_object = Award.objects.filter(id=award_edited_object[index])
                            if raw_existing_object:
                                existing_object = raw_existing_object.first()
                                existing_object.award_name = award_dict.get("award")[index]
                                existing_object.rtl_award_name = award_dict.get("rtl_award")[index]
                                existing_object.award_year = award_dict.get("award_year")[index]
                                existing_object.save()
                    except IndexError:
                        create_new_award(award_dict, doctor, index)
        else:
            for index in range(input_length):
                create_new_award(award_dict, doctor, index)
    except Exception as e:
        print('value fo error in save award')
        print(e)


def create_new_award(award_dict, doctor, index):
    Award.objects.create(
        doctor=doctor,
        award_name=award_dict.get("award")[index],
        rtl_award_name=award_dict.get("rtl_award")[index],
        award_year=award_dict.get("award_year")[index],
    )


def save_user_doctor(user, doctor, user_raw_data):
    print("inside the save_user_doctor")
    print("user :", user)
    print("doctor : ", doctor)
    try:
        user.full_name = user_raw_data.get("name")
        user.rtl_full_name = user_raw_data.get("rtl_name")
        # for makeing phone read only (we don't update this phone number)
        # user.phone = user_raw_data.get("phone")
        user.email = user_raw_data.get("email")
        user.date_of_birth = user_raw_data.get("dob")
        user.gender = user_raw_data.get("gender")
        user.save()
        doctor.fee = user_raw_data.get("fee")
        doctor.title = DoctorTitle.objects.get(id=user_raw_data.get("title"))
        doctor.doc_license_no = user_raw_data.get("license_no")
        doctor.bio = user_raw_data.get("bio")
        doctor.farsi_bio = user_raw_data.get("bio_farsi")
        doctor.pashto_bio = user_raw_data.get("bio_pashto")
        doctor.save()
    except Exception as e:
        print('value of error in save user doctor')
        print(e)


class DoctorProfile(View):
    template_name = "doctor/doctor_profile.html"
    data = {
        "doctor_object": "",
        "cities": City.objects.all(),
        "titles": DoctorTitle.objects.all(),
        "clinics": Clinic.objects.all(),
        "specialities": Speciality.objects.all(),
        "degrees": DegreeType.objects.all(),
    }

    def get_data(self):
        user = self.request.user
        print('value of user and it is avatar')
        print(user)
        is_doctor = Doctor.objects.filter(user=user)
        if is_doctor.exists():
            doctor = is_doctor.first()
            self.data.update({"doctor_object": doctor})
        return self.data

    def get(self, request, *args, **kwargs):
        get_dict = self.get_data()
        return render(request, self.template_name, get_dict)

    def post(self, request, *args, **kwargs):
        # get_dict = self.get_data()
        print("the post function got called ")
        print(request.POST)
        if request.method == "POST":
            print("the method is POST")
            post_data = dict(request.POST)
            raw_data = request.POST
            print('value of raw_data=====------')
            print(raw_data)
            user = self.request.user
            doctor = user.doctor
            if raw_data.get('operation') == 'save_changes' or raw_data.get('operation') == 'submit_for_review':
                print('it is the save changes and review')
                save_user_doctor(user, doctor, raw_data)
                professional_profile(post_data, doctor)
                save_clinic(post_data, doctor, self.request)
                save_education(post_data, doctor, self.request)
                save_experience(post_data, doctor, self.request)
                save_award(post_data, doctor, self.request)
                save_user_address(raw_data, user)
                if raw_data.get('operation') == 'submit_for_review':
                    doctor.professional_status = False
                    doctor.is_profile_on_progress = True
                    doctor.save()
            else:
                doctor.professional_status = False
                doctor.is_profile_on_progress = False
                doctor.save()
            
        return redirect("doctor:doctor_profile")


class SocialMediaProfile(FormView):
    model = DoctorSocialMedia
    form_class = SocialMediaForm
    success_url = "."
    template_name = "doctor/social_media_profile.html"


class DoctorChangePassword(PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = "doctor/doctor_change_password.html"


def load_services(request):
    specialities_id = request.GET.get("specialities_id")
    specialities_dict = eval(specialities_id)
    # output: {'specialities_id': ['1', '3', '4']}
    service_object_list = []
    if specialities_dict["specialities_id"]:
        for speciality_id in specialities_dict["specialities_id"]:
            # lookup = Q(id=service_id) # find a way to do it like this
            speciality_object = Speciality.objects.get(id=speciality_id)
            qs = Service.objects.filter(speciality=speciality_object)
            service_object_list.extend(qs)
        return render(request, "doctor/dropdowns/services_dropdown.html", {"ajax_services": service_object_list})
    else:
        return render(request, "doctor/dropdowns/services_dropdown.html", {})


def load_conditions(request):
    print("INSIDE load conditions page ")
    specialities_id = request.GET.get("specialities_id")
    specialities_dict = eval(specialities_id)
    # output: {'specialities_id': ['1', '3', '4']}
    condition_object_list = []
    if specialities_dict["specialities_id"]:
        for speciality_id in specialities_dict["specialities_id"]:
            speciality_object = Speciality.objects.get(id=speciality_id)
            qs = Service.objects.filter(speciality=speciality_object)
            condition_object_list.extend(qs)
        return render(
            request,
            "doctor/dropdowns/conditions_dropdown.html",
            {"ajax_conditions": condition_object_list},
        )
    # for sp_id in specialities_dict["specialities_id"]:
    #     speciality_object = Speciality.objects.get(id=sp_id)
    #     # qs = Condition.objects.filter(service=service_object)
    #     qs = Service.objects.filter(speciality=speciality_object)
    #     condition_object_list.extend(qs)
    # # print(len(condition_object_list))
    # return render(
    #     request,
    #     "doctor/dropdowns/conditions_dropdown.html",
    #     {"ajax_conditions": condition_object_list},
    # )
    
def load_degrees(request):
    print("vlaue fo get_json_city")
    degrees = DegreeType.objects.all()
    post_list = serializers.serialize("json", degrees)
    return HttpResponse(post_list, content_type="application/json")


def load_degree_names(request):
    degree_id = request.GET.get("degree_id")
    print("vlaue fo degree_id --- ")
    print(degree_id)
    degree = DegreeType.objects.get(id=degree_id)
    education_degrees = EducationDegree.objects.filter(degree_type=degree)
    post_list = serializers.serialize("json", education_degrees)
    return HttpResponse(post_list, content_type="application/json")


def load_json_districts(request):
    city_id = request.GET.get("city_id")
    print("vlaue fo city_id")
    print(city_id)
    city = City.objects.get(id=city_id)
    districts = District.objects.filter(city=city)
    post_list = serializers.serialize("json", districts)
    return HttpResponse(post_list, content_type="application/json")


def get_json_city(request):
    print("vlaue fo get_json_city")
    cities = City.objects.all()
    post_list = serializers.serialize("json", cities)
    return HttpResponse(post_list, content_type="application/json")


def doctor_review_view(request, *args, **kwargs):
    reply_form = forms.CreateFeedBackRepliesForm()
    user_is = lambda user: request.user.user_type == user
    if not user_is("Doctor"):
        return HttpResponseForbidden()

    if request.POST.get("submit") == "create-reply":
        try:
            feedback = request.POST.get("comment-id")
            reply = request.POST.get("reply", None)
            feedback_id = request.POST.get("comment-id", None)
            print('value of reply============----')
            print(reply)
            print(feedback_id)
            # reply_form = forms.CreateFeedBackRepliesForm({"feedback": feedback, "author": request.user, "reply": reply})
            if reply is not None and reply != '' and feedback_id is not None and feedback_id != '':
                # now sending the notification to the patient
                feedback_object = Feedback.objects.get(id=feedback_id)
                appt_object = feedback_object.appointment
                review_relplied_by_doctor(appt_object, reply)
                
                # create reply
                FeedbackReplies.objects.create(
                    feedback = feedback_object, author=request.user, reply=reply
                )

                return JsonResponse(
                    {
                        "status": "success",
                        "comment_id": feedback,
                        "reply": reply,
                        "user_pic": request.user.avatar.url,
                        "user_name": str(request.user),
                    }
                )
            else:
                return JsonResponse({'status': 'fail'})
        except Exception as e:
            print('vallue fo erroro in view 000-----')
            return JsonResponse({'status': 'fail'})

    comments = Feedback.objects.filter(appointment__doctor__user=request.user).order_by("-timestamp")
    # paginator
    paginator = Paginator(comments, 10)
    page = request.GET.get("page")
    comments = paginator.get_page(page)
    doctor_data = {
        "main_doctor": request.user,
        "comments": comments,
        "reply_form": reply_form,
    }
    return render(request, "doctor/doctor_review.html", doctor_data)


class ReviewDetailView(DetailView):
    model = Feedback
    template_name = "doctor/templatetag_files/doctor_single_feedback.html"

    def post(self, request, *args, **kwargs):
        feedback = request.POST.get("comment-id")
        reply = request.POST.get("reply")
        reply_form = forms.CreateFeedBackRepliesForm({"feedback": feedback, "author": request.user, "reply": reply})
        if reply_form.is_valid():
            reply_form.save()
            # now sending the notification to the patient
            # notifications_manager.create_feedback_relay(feedback=feedback, replay=reply)
            
            # review_relplied_by_doctor(appt_object, reply)
            response = {
                "status": "success",
                "comment_id": feedback,
                "reply": reply,
                "user_pic": request.user.avatar.url,
                "user_name": str(request.user),
            }
            return JsonResponse(response)


def add_appointment_condition_thread(request):
    if request.method == "POST":
        form = ApptConditionTreatForm(request.POST)
        print("now add_appointment_condition_thread FORM is ", form.is_valid())
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "fail"})


