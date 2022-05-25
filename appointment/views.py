from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.contrib.auth import get_user_model
import calendar
from django.db.models import Q
from datetime import datetime, date, timedelta, time as datetime_time

# exprot to pdf packages
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from notification.models import Notification

User = get_user_model()
from django.core import serializers

from user.models import Doctor, Patient, Relative
from home.models import CityManager
from .models import Appointment, ApptQrCode, DaySchedulePattern, DeactivatedApptSlot, WeekDays, schedule_by_a_pattern
from doctor.models import Clinic
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from notification import notification_manager as notification_manager



def schedule_automation(self, doctor, request):
    is_day_patter_exist = True
    for clinic in doctor.clinic_set.all():
        week_day_pattern = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic).order_by('id')
        
        if not week_day_pattern.exists():
            is_day_patter_exist = False
            break;
        else:
            print('another day scheclue patter')
            self.schedule_by_pattern(doctor, clinic, request, "automate")
    return is_day_patter_exist


def clear_previous_qr_img(doctor):
    today_date = date.today()
    previous_slot = ApptQrCode.objects.filter(doctor=doctor, appt_slot__appt_date__lt=today_date)
    if previous_slot.exists():
        print("prevoiuse slot is exist")
        previous_slot.delete()


class PublicTimeSlot(View):
    template_name = "appointment/public_time_slot.html"
    model = Appointment
    get_object = lambda self: get_object_or_404(User, id=self.kwargs.get("doctor_id"))

    def get(self, request, *args, **kwargs):
        context = {
            'booked_clinic_id': 'no_clinic_selected',
            'booked_appt_id': 'no_appt_selected',
        }
        try:
            today_date = date.today()
            doctor = get_object_or_404(Doctor, user=self.get_object())
            self.model.objects.clear_history()
            if doctor is not None:
                is_all_good = schedule_automation(self.model.objects, doctor, self.request)
                if not is_all_good:
                    messages.warning(request, 'Doctor has not schedudle appointments to any of his clinics yet.')
                    return redirect(request.META.get('HTTP_REFERER'))
            
            if request.user.is_authenticated:
                has_booked_appt = self.model.objects.filter(
                    patient=request.user.patient, doctor=doctor, status=Appointment.ApptStatus.BOOKED, appt_date__gte=today_date
                )
            
                if has_booked_appt.exists():
                    print("has_booked_appt.exists() is true")
                    context["booked_clinic_id"] = has_booked_appt.first().clinic.id
                    context["booked_appt_id"] = has_booked_appt.first().id
                
            context["user_object"] = self.get_object()
            context["today_weekday"] = calendar.day_name[today_date.weekday()]
        except Exception as e:
            messages.warning(request, 'Unexpected error occured, please try again')
            return redirect(request.META.get('HTTP_REFERER'))
        return render(request, self.template_name, context)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("user:login")
        return super(self.__class__, self).dispatch(request, *args, **kwargs)


class ReScheduleAppointment(View):
    template_name = "appointment/reschedule_appointment.html"
    model = Appointment
    get_object = lambda self: get_object_or_404(User, id=self.kwargs.get("doctor_id"))

    def get(self, request, *args, **kwargs):
        today_date = date.today()
        # patient_user = self.request.user
        context = {
            'booked_clinic_id': 'no_clinic_selected',
            'booked_appt_id': 'no_appt_selected',
        }
        try:
            self.model.objects.clear_history()
            doctor = get_object_or_404(Doctor, user=self.get_object())
            if doctor is not None:
                is_all_good = schedule_automation(self.model.objects, doctor, self.request)
                if not is_all_good:
                    messages.warning(request, 'Doctor has not schedudle appointments to any of his clinics yet.')
                    return redirect(request.META.get('HTTP_REFERER'))
            if request.user.is_authenticated:
                has_booked_appt = self.model.objects.filter(
                    patient=request.user.patient, doctor=doctor, status=Appointment.ApptStatus.BOOKED, appt_date__gte=today_date
                )
            
                if has_booked_appt.exists():
                    context["booked_clinic_id"] = has_booked_appt.first().clinic.id
                    context["booked_appt_id"] = has_booked_appt.first().id
            
            context["user_object"] = self.get_object()
            context["today_weekday"] = calendar.day_name[today_date.weekday()]
        except:
            messages.warning(request, 'Unexpected error occured, please try again')
            return redirect(request.META.get('HTTP_REFERER'))
        return render(request, self.template_name, context)


class TodayDoctorApptList(DetailView):
    template_name = "appointment/today_booked_appt_patient_list.html"
    model = ApptQrCode

    def get_object(self):
        raw_clinic_id = self.kwargs.get("clinic_id")
        is_clinic = Clinic.objects.filter(id=raw_clinic_id)
        today_date = date.today()
        clinic = None
        clinic_booked_appt_list = None
        if is_clinic.exists():
            clinic = is_clinic.first()
        doctor = self.request.user.doctor
        if doctor and clinic:
            clinic_booked_appt_list = self.model.objects.filter(
                appt_slot__doctor=doctor,
                appt_slot__clinic=clinic,
                appt_slot__patient__isnull=False,
                appt_slot__appt_date__gte=today_date,
            )
        return {
            "clinic": clinic,
            "clinic_booked_appt_list": clinic_booked_appt_list,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_data = self.get_object()
        context["clinic"] = get_object_data["clinic"]
        if get_object_data["clinic_booked_appt_list"] is not None:
            context["clinic_booked_appt_list"] = get_object_data["clinic_booked_appt_list"]
        return context


# booking by patient and resechdule 
def book_appointment(request, *args, **kwargs):
    the_response = 'success'
    try:
        if request.method == "POST":
            post = request.POST
            relative = None
            app = get_object_or_404(Appointment, id=post.get("new_app"))
            patient = get_object_or_404(Patient, user__id=post.get("patient"))
            if str(patient.user.id) != post.get('relative', None):
                relative = get_object_or_404(Relative, user__id=post.get("relative"))
     
            is_reschedule = post.get('reschedule')
            def already_booked_appointment_with_doctor_today(doctor, patient, relative):
                is_exist = False
                has_today_app = Appointment.objects.filter(
                    patient=patient, relative=relative, doctor=doctor, booked_at__date=datetime.today().date()
                )
                if has_today_app:
                    if is_reschedule == '1':
                        has_today_app.update(
                            patient=None,
                            relative=None,
                            status=Appointment.ApptStatus.PENDING,
                        )
                    else:
                        is_exist= True
                return is_exist

            if already_booked_appointment_with_doctor_today(app.doctor, patient, relative):
                return JsonResponse({"status": "already-booked"})
            
            if relative:
                app.patient, app.relative, app.status = patient, relative, Appointment.ApptStatus.BOOKED
            else:
                app.patient, app.status = patient, Appointment.ApptStatus.BOOKED
            app.save()
            # now creating the qrcode of the appointment
            ApptQrCode.objects.update_or_create(appt_slot=app)
            return JsonResponse({"status": the_response, "appid": app.id})
    except Exception as e:
        the_response = 'fail'
    return JsonResponse({"status": the_response})


class BookSucceed(TemplateView):
    template_name = "appointment/booked_success.html"

    def get_context_data(self, **kwargs):
        context = super(BookSucceed, self).get_context_data(**kwargs)
        appid = kwargs.get("appid")
        appointment = get_object_or_404(Appointment, id=appid, patient=self.request.user.patient)
        context["appointment"] = appointment
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("appointment-success-notification"):
            app = Appointment.objects.get(id=request.POST.get("appointment-success-notification"))
            # notification_manager.booked_appointment_notification_to_doctor(app.id)
        return JsonResponse({"status": "success"})


# def booking_by_patient(request, *args, **kwargs):
#     print("inside the booking_by_patient")
#     print(request.user)
#     print(request.POST)
#     appt_object = Appointment.objects
#     if request.method == "POST":
#         print("request is post")
#         raw_data = request.POST
#         patient_user = request.user
#         get_json_data = toggle_booking_slot(appt_object, raw_data, patient_user)
#         return JsonResponse(get_json_data)
#     return HttpResponse("Failed To Activate/Deactivate Appt Slot", status=404)


# def toggle_booking_slot(self, raw_data, patient_user, relative_user=None):
#     data_dict = {
#         "active_start_time": "",
#         "active_end_time": "",
#         "deactive_start_time": "",
#         "deactive_end_time": "",
#         "response_error": "",
#     }
#     doctor_user_id = raw_data.get("doctor_user_id")
#     doctor_object = None
#     deactive_slot = None
#     this_patient_appt_count = 0
#     doctor_user_object = User.objects.filter(id=doctor_user_id)
#     doctor_object_raw = Doctor.objects.filter(user=doctor_user_object.first())
#     if doctor_user_object.exists() and doctor_object_raw.exists():
#         doctor_object = doctor_object_raw.first()
#     if self.filter(patient=patient_user.patient).exists():
#         this_patient_appt_count = self.filter(patient=patient_user.patient).exclude(doctor=doctor_object).count()
#         print("value of this_patient_appt_count", this_patient_appt_count)
#     if this_patient_appt_count >= 3:
#         data_dict.update({"response_error": "You cannot get more than three appointments in a single day"})
#     else:
#         if raw_data.get("deactive_slot_id"):
#             print("deactive_slot is empty ... finally checked this condition as well ")
#             deactive_slot = self.filter(id=raw_data.get("deactive_slot_id"), doctor=doctor_object)
#         active_slot = self.filter(id=raw_data.get("active_slot_id"), doctor=doctor_object)
#         if active_slot.exists():
#             active_slot_object = active_slot.first()
#             active_slot_object.patient = patient_user.patient
#             if relative_user is not None:
#                 active_slot_object.relative = relative_user
#             active_slot_object.status = Appointment.ApptStatus.BOOKED
#             active_slot_object.save()
#             data_dict.update({"active_start_time": str(active_slot_object.start_appt_time)})
#             data_dict.update({"active_end_time": str(active_slot_object.end_appt_time)})
#             # create qr code
#             create_appt_qr(active_slot_object, doctor_object, patient_user.patient, active_slot_object.clinic)
#             # deactive_slot
#         if deactive_slot is not None:
#             deactivate_slot_object = deactive_slot.first()
#             deactivate_slot_object.patient = None
#             deactivate_slot_object.status = Appointment.ApptStatus.PENDING
#             deactivate_slot_object.save()
#             data_dict.update({"deactive_start_time": str(deactivate_slot_object.start_appt_time)})
#             data_dict.update({"deactive_end_time": str(deactivate_slot_object.end_appt_time)})
#             # delete qr code
#             appt_qr_object = ApptQrCode.objects.filter(appt_slot=deactivate_slot_object)
#             if appt_qr_object.exists():
#                 deactive_slot_qr = appt_qr_object.first()
#                 deactive_slot_qr.delete()

#     return data_dict


# def create_appt_qr(appt_slot, doctor, patient, clinic):
#     ApptQrCode.objects.create(
#         appt_slot=appt_slot,
#         doctor=doctor,
#         patient=patient,
#         clinic=clinic,
#     )


def cancel_appt_by_patient(request, *args, **kwargs):
    doctor_object = None
    appt_object = Appointment.objects
    data_dict = {
        "clinic_id": "",
        "appt_start_time": "",
        "appt_end_time": "",
        "response_error": "",
    }
    if request.method == "POST":
        doctor_user_id = request.POST.get("doctor_user_id")
        appt_slot_id = request.POST.get("cancel_appt_slot_id")

        doctor_user_object = User.objects.filter(id=doctor_user_id)
        doctor_object_raw = Doctor.objects.filter(user=doctor_user_object.first())

        if doctor_user_object.exists() and doctor_object_raw.exists():
            doctor_object = doctor_object_raw.first()

        active_slot = appt_object.filter(id=appt_slot_id, doctor=doctor_object)
        if active_slot.exists() and doctor_object_raw.exists():
            active_slot_object = active_slot.first()
            active_slot_object.patient = None
            active_slot_object.status = Appointment.ApptStatus.PENDING
            active_slot_object.save()
            data_dict.update({"appt_start_time": str(active_slot_object.start_appt_time)})
            data_dict.update({"appt_end_time": str(active_slot_object.end_appt_time)})
            data_dict.update({"clinic_id": str(active_slot_object.clinic.id)})
        else:
            data_dict.update({"response_error": "slot_not_exist"})
        return JsonResponse(data_dict)
    return HttpResponse("Failed To Activate/Deactivate Appt Slot", status=404)


class ScheduleTime(View):
    template_name = "appointment/schedule_time.html"

    def get(self, request, *args, **kwargs):
        today_date = date.today()
        today_weekday = calendar.day_name[today_date.weekday()]
        appt_object = Appointment.objects
        user = request.user
        is_doctor = Doctor.objects.filter(user=user)
        if is_doctor.exists():
            doctor = is_doctor.first()
            # clear_previous_qr_img(doctor)
            appt_object.clear_history()
            schedule_automation(appt_object, doctor, request)
        return render(request, self.template_name, {"today_weekday": today_weekday})

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            raw_data = request.POST
            user = request.user
            is_doctor = Doctor.objects.filter(user=user)
            is_clinic = Clinic.objects.filter(id=raw_data.get("clinic_id"))
            if is_doctor.exists() and is_clinic.exists():
                clinic = is_clinic.first()
                doctor = is_doctor.first()
                response_data = schedule_for_everyday(doctor, clinic, raw_data, request)
                return JsonResponse(response_data)
        return HttpResponse("Failed To Access Schedules", status=404)


def schedule_for_everyday(doctor, clinic, raw_data, request):
    appt_object = Appointment.objects
    week_days = WeekDays.objects.all()
    for day in week_days:
        create_day_pattern(doctor, clinic, day, raw_data)
    appt_object.schedule_by_pattern(doctor, clinic, request, "manual")
    response_data = get_json_appt(appt_object, clinic, doctor)
    return response_data


def get_json_appt(self, clinic, doctor):
    today_date = date.today()
    this_clinic_appt = self.filter(clinic=clinic, doctor=doctor, appt_date__gte=today_date)
    this_clinic_schedule = DaySchedulePattern.objects.filter(clinic=clinic, doctor=doctor)
    schedule_dict = {}
    if this_clinic_schedule.exists():
        for clinic_schedule in this_clinic_schedule:
            schedule_dict.update({str(clinic_schedule.week_day): clinic_schedule.active})
    appt_list = []
    if this_clinic_appt.exists():
        for appt_object in this_clinic_appt:
            data_dict = {
                "clinic_id": appt_object.clinic.id,
                "day_pattern": str(appt_object.day_pattern.week_day),
                "start_appt_time": str(appt_object.start_appt_time),
                "end_appt_time": str(appt_object.end_appt_time),
                "active": appt_object.active,
            }
            appt_list.append(data_dict)
    response_data = {
        "schedule_dict": schedule_dict,
        "appt_list": appt_list,
    }
    return response_data


def create_day_pattern(doctor, clinic, day, raw_data):
    raw_start_time = raw_data.get("slot_start")
    raw_end_time = raw_data.get("slot_end")
    start_time_data = timedelta(hours=int(raw_start_time[:2]), minutes=int(raw_start_time[3:5]))
    end_time_data = timedelta(hours=int(raw_end_time[:2]), minutes=int(raw_end_time[3:5]))
    slot_duration_data = timedelta(days=0, minutes=int(raw_data.get("slot_duration")))
    is_weekday_pattern = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic, week_day=day)
    if is_weekday_pattern.exists():
        weekday_pattern = is_weekday_pattern.first()
        weekday_pattern.time_slot_duration = slot_duration_data
        weekday_pattern.start_day_time = start_time_data
        weekday_pattern.end_day_time = end_time_data
        weekday_pattern.save()
    else:
        DaySchedulePattern.objects.create(
            week_day=day,
            time_slot_duration=slot_duration_data,
            start_day_time=start_time_data,
            end_day_time=end_time_data,
            doctor=doctor,
            clinic=clinic,
        )


def schedule_custom_day_pattern(request, *args, **kwargs):
    if request.method == "POST":
        try:
            raw_data = request.POST
            user = request.user
            is_doctor = Doctor.objects.filter(user=user)
            is_clinic = Clinic.objects.filter(id=raw_data.get("clinic_id"))
            is_day = WeekDays.objects.filter(week_day=raw_data.get("day_pattern"))
            if is_doctor.exists() and is_clinic.exists() and is_day.exists():
                clinic = is_clinic.first()
                doctor = is_doctor.first()
                appt_object = doctor.appointment_set.all()
                day = is_day.first()
                appt_list = schedule_particular_day(doctor, clinic, day, raw_data, appt_object, 'web_request')
                return JsonResponse({"appt_list": appt_list})
        except Exception as e:
            pass
        return JsonResponse({"appt_list": 'error'})
        # return HttpResponse("Failed To Scheduel For A Particular Day", status=404)

def schedule_particular_day(doctor, clinic, day, raw_data, appt_queryset, request_type):
    today_date = date.today()
    # is_there_booked_queryset = appt_queryset.filter(clinic=clinic, )
    create_day_pattern(doctor, clinic, day, raw_data)
    slotting_by_particular_pattern(appt_queryset, clinic, doctor, day)
    # get value and send over to template
    if request_type == 'web_request':
        day_schedule_pattern_object = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic, week_day=day)
        if day_schedule_pattern_object.exists():
            pattern = day_schedule_pattern_object.first()
            particular_day = appt_queryset.filter(clinic=clinic, day_pattern=pattern, appt_date__gte=today_date)
            if particular_day.exists():
                appt_list = []
                for a_day in particular_day:
                    data_dict = {
                        "clinic_id": a_day.clinic.id,
                        "day_pattern": str(a_day.day_pattern.week_day),
                        "start_appt_time": str(a_day.start_appt_time),
                        "end_appt_time": str(a_day.end_appt_time),
                    }
                    appt_list.append(data_dict)
                return appt_list
                # return JsonResponse({"appt_list": appt_list})


def slotting_by_particular_pattern(self, clinic, doctor, day):
    today_date = date.today()
    day_schedule_pattern_object = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic, week_day=day)
    if day_schedule_pattern_object.exists():
        pattern = day_schedule_pattern_object.first()
        if not pattern.active:
            pattern.active = True
            pattern.save()
        deactivated_slot_object = DeactivatedApptSlot.objects.filter(doctor=doctor, clinic=clinic, day_pattern=pattern)
        if deactivated_slot_object.exists():
            deactivated_slot_object.delete()
        schedule_by_a_pattern(self, pattern, today_date, clinic, doctor, "manual")


# Toggle the day of a clinic////
def toggle_day_pattern(request, *args, **kwargs):
    if request.method == "POST":
        raw_data = request.POST
        user = request.user
        is_doctor = Doctor.objects.filter(user=user)
        is_clinic = Clinic.objects.filter(id=raw_data.get("clinic_id"))
        is_day = WeekDays.objects.filter(week_day=raw_data.get("day_pattern"))
        if is_doctor.exists() and is_clinic.exists() and is_day.exists():
            clinic = is_clinic.first()
            doctor = is_doctor.first()
            day = is_day.first()
            appt_object = Appointment.objects
            toggle_week_day_activation(doctor, clinic, day, appt_object)
            # does not belong to api
            appt_list = []
            is_active = False
            modified_pattern = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic, week_day=day)
            if modified_pattern.exists() and modified_pattern.first().active:
                is_active = True
                appt_object_list = appt_object.filter(doctor=doctor, clinic=clinic, day_pattern=modified_pattern.first())
                if appt_object_list.exists():
                    for a_day in appt_object_list:
                        data_dict = {
                            "clinic_id": a_day.clinic.id,
                            "day_pattern": str(a_day.day_pattern.week_day),
                            "start_appt_time": str(a_day.start_appt_time),
                            "end_appt_time": str(a_day.end_appt_time),
                        }
                        appt_list.append(data_dict)
            data_dict = {
                "is_pattern_active": is_active,
                "appt_list": appt_list,
            }
            return JsonResponse(data_dict)
        return HttpResponse("succes form view schedule_custom_day_pattern ")

def toggle_week_day_activation(doctor, clinic, day, appt_object):
    print('inside the toggle_week_day_activation')
    day_schedule_pattern_object = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic, week_day=day)
    if day_schedule_pattern_object.exists():
        pattern = day_schedule_pattern_object.first()
        if not pattern.active:
            slotting_by_particular_pattern(appt_object, clinic, doctor, day)
        else:
            pattern.active = False
            pattern.save()
            clear_this_day_pattern_appt(appt_object, doctor, clinic, pattern)

def clear_this_day_pattern_appt(self, doctor, clinic, pattern):
    today_date = date.today()
    this_pattern_appt = self.filter(
        doctor=doctor, clinic=clinic, day_pattern=pattern, appt_date__gte=today_date
        ).filter(~Q(status=Appointment.ApptStatus.COMPLETED))
    deactivated_slot_object = DeactivatedApptSlot.objects.filter(doctor=doctor, clinic=clinic, day_pattern=pattern)
    if deactivated_slot_object.exists():
        deactivated_slot_object.delete()
    if this_pattern_appt.exists():
        is_patient_book_to_pattern = this_pattern_appt.filter(~Q(patient=None) | ~Q(relative=None) & Q(status=Appointment.ApptStatus.BOOKED))
        if is_patient_book_to_pattern.exists():
            for patr_obj in is_patient_book_to_pattern:
                notification_manager.appt_canceled_by_doctor(patr_obj)
        this_pattern_appt.delete()


# Deactivate a slot from a particular day of the week
def toggle_appt_slot(request, *args, **kwargs):
    appt_object = Appointment.objects
    if request.method == "POST":
        raw_data = request.POST
        user = request.user
        raw_start_time = raw_data.get("start_appt_time")
        is_doctor = Doctor.objects.filter(user=user)
        is_clinic = Clinic.objects.filter(id=raw_data.get("clinic_id"))
        is_day = WeekDays.objects.filter(week_day=raw_data.get("day_pattern"))
        if is_doctor.exists() and is_clinic.exists() and is_day.exists():
            clinic = is_clinic.first()
            doctor = is_doctor.first()
            day = is_day.first()
            a_slot_appt = toggle_and_track(appt_object, doctor, clinic, day, raw_start_time)
            data_dict = {
                "clinic_id": a_slot_appt.clinic.id,
                "day_pattern": str(a_slot_appt.day_pattern.week_day),
                "start_appt_time": str(a_slot_appt.start_appt_time),
                "end_appt_time": str(a_slot_appt.end_appt_time),
                "active": a_slot_appt.active,
            }
            return JsonResponse(data_dict)
    return HttpResponse("Failed To Activate/Deactivate Appt Slot", status=404)


def toggle_and_track(self, doctor, clinic, day, raw_start_time):
    schedule_pattern_object = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic, week_day=day)
    start_hour_appt = None
    start_minute_appt = None
    try:
        start_hour_appt = int(raw_start_time[:2])
        start_minute_appt = int(raw_start_time[3:5])
    except ValueError:
        start_hour_appt = int("0{}".format(raw_start_time[:1]))
        start_minute_appt = int(raw_start_time[2:4])

    if schedule_pattern_object.exists() and raw_start_time:
        start_time_data = timedelta(hours=start_hour_appt, minutes=start_minute_appt)
        pattern = schedule_pattern_object.first()
        is_slot_exist = self.filter(doctor=doctor, clinic=clinic, day_pattern=pattern, start_appt_time=start_time_data)

        if is_slot_exist.exists():
            selected_slot = is_slot_exist.first()
            if selected_slot.active:
                selected_slot.active = False
                track_deactivated_slot("deactivate", doctor, clinic, start_time_data, pattern)
                # now if selected_slot is booked, send the cancelled notification to patient
                if selected_slot.patient:
                    selected_slot.patient, selected_slot.relative = None, None
                    selected_slot.status = Appointment.ApptStatus.PENDING
                    ApptQrCode.objects.filter(appt_slot=selected_slot).delete()
                    notification_manager.doctor_canceled_appointment(selected_slot.id)
            else:
                selected_slot.active = True
                track_deactivated_slot("activate", doctor, clinic, start_time_data, pattern)
            selected_slot.save()
            get_this_slot = self.filter(doctor=doctor, clinic=clinic, start_appt_time=start_time_data, day_pattern=pattern)
            if get_this_slot.exists():
                return get_this_slot.first()
    return None


def track_deactivated_slot(operation, doctor, clinic, start_time_data, pattern):
    deactivated_slot = DeactivatedApptSlot.objects.filter(
        doctor=doctor, clinic=clinic, start_appt_time=start_time_data, day_pattern=pattern
    )
    if operation == "deactivate":
        DeactivatedApptSlot(doctor=doctor, clinic=clinic, day_pattern=pattern, start_appt_time=start_time_data).save()
    else:
        if deactivated_slot.exists():
            deactivated_slot.delete()
