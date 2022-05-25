from cgitb import lookup

from django.dispatch import receiver
from DoctorPlus.utils import free_service_checker, get_feedback_percentage, is_valid_field_with_or
from doctor.views import professional_profile
from appointment.views import schedule_automation, schedule_for_everyday, schedule_particular_day, toggle_week_day_activation, track_deactivated_slot
from ast import Str
from rest_framework import fields, status
import json
from rest_framework import mixins, serializers, views
from home.models import Address, City, District
# from patient.templatetags.patient_tags import patiet_last_chat
import doctor
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.mixins import *
from rest_framework import permissions
from datetime import date, datetime, timedelta
from notification import notification_manager as notification_manager
from rest_api.patient_api.serializers import FeedbackDataSerializer
from rest_api.user_api.permissins import AnonPermissionOnly, IsOwnerOrReadOnlyDoctor, IsOwnerOrReadOnly

from drf_multiple_model.views import ObjectMultipleModelAPIView

from django.db.models import Q, F
from django.core import serializers as core_serializer

# import datetime
import itertools

from rest_api.utils.pagination import CustomPagination
from . import serializers as ser

from appointment.models import (
    Appointment,
    ApptConditionTreat,
    ApptQrCode,
    Feedback,
    FeedbackReplies,
    DaySchedulePattern,
    WeekDays,
    DeactivatedApptSlot,
)
from user.models import Condition, DoctorTitle, FreeServiceSchedule, Patient, Relative, Service, Speciality, User, Doctor
from medicalrecord.models import MedicalRecords
from notification.models import Notification
from doctor.models import Clinic, Award, DegreeType, EducationDegree, Experience, Education

# ============== # =====================
# Eblis Edition


class ClinicScheduleBrief(generics.ListAPIView):
    serializer_class = ser.ClinicScheduleBriefSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        message = 'success'
        try:
            doctor = self.request.user.doctor
            my_clinic = doctor.clinic_set.all()
            # 
            the_queryset = []
            for the_clinic in my_clinic:
                clinic_weekly_schedule = the_clinic.dayschedulepattern_set.filter(doctor=doctor)
                if clinic_weekly_schedule.exists():
                    for day_schedule in clinic_weekly_schedule:
                        is_true = is_usual_schedule_day(day_schedule, clinic_weekly_schedule)
                        if is_true:
                            break
                    total_booked_appt_no = doctor.appointment_set.filter(status=Appointment.ApptStatus.BOOKED, clinic=the_clinic).count()
                    if not any(query_data['id'] == the_clinic.id for query_data in the_queryset):
                        the_queryset.append({
                            'id': the_clinic.id,
                            'clinic_name': the_clinic.clinic_name,
                            'rtl_clinic_name': the_clinic.rtl_clinic_name,
                            'time_slot_duration': day_schedule.time_slot_duration,
                            'start_day_time': day_schedule.start_day_time,
                            'end_day_time': day_schedule.end_day_time,
                            'total_booked_appt_no': total_booked_appt_no or 0,
                        })
                else:
                    print('first time to schedule')
                    the_queryset.append({
                        'id': the_clinic.id,
                        'clinic_name': the_clinic.clinic_name,
                        'rtl_clinic_name': the_clinic.rtl_clinic_name,
                        'time_slot_duration': '00:00:00',
                        'start_day_time': '00:00:00',
                        'end_day_time': '00:00:00',
                        'total_booked_appt_no': 0,
                    })
                    
        except Exception as e:
            message = 'fail'
            the_queryset = Clinic.objects.none()
            print('alue of erororororo0000')
            print(e)
        the_data = self.get_serializer(the_queryset, many=True).data
        return Response(the_data, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)

def is_usual_schedule_day(day_schedule, week_schedule):
    repeatation = 0
    for a_day in week_schedule:
        if (a_day.time_slot_duration == day_schedule.time_slot_duration 
            and a_day.start_day_time == day_schedule.start_day_time 
            and a_day.end_day_time == day_schedule.end_day_time):
            repeatation += 1
    if repeatation >= 2:
        return True
    return False


class ClinicApptAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes       = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class         = ser.ClinicApptSerializer
    
    def get_data(self, request):
        message = 'success'
        try:
            doctor = request.user.doctor
            today_date = date.today()
            Appointment.objects.clear_history()
            schedule_automation(Appointment.objects, doctor, request)
            # //
            clinic_id = request.GET.get('clinic_id')
            week_day = request.GET.get('week_day')
            
            print('value fo request.GET')
            print(request.GET)
            the_filter = Q(~Q(status=Appointment.ApptStatus.COMPLETED) & Q(appt_date__gte=today_date) & Q(clinic__id=clinic_id))
            if week_day is not None:
                    the_filter.add(Q(day_pattern__week_day__week_day=week_day), Q.AND)
            appt_queryset = doctor.appointment_set.filter(the_filter)
        except Exception as e:
            appt_queryset = Appointment.objects.none()
            message = 'fail'
        print('value fo appt_queryset the length bro')
        print(len(appt_queryset))
        the_response = self.get_serializer(appt_queryset, many=True).data
        return the_response, message

    def get(self, request, *args, **kwargs):
        # get appt of a clinic or a clinic with a specific day 
        the_response, message = self.get_data(self.request)
        return Response(the_response, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
        

    def post(self, request, *args, **kwargs):
        raw_data = request.data
        operation = raw_data.get('operation', None)
        # toggle_day, toggle_slot, schedule_all, schedule_day
        # 351_tackle dealt
        print('value of request.data')
        print(request.data)
        message = 'success'
        try:
            doctor =  request.user.doctor
            clinic = Clinic.objects.get(id=raw_data.get("clinic_id"))
            appt_queryset = doctor.appointment_set.filter(~Q(status=Appointment.ApptStatus.COMPLETED))
            if operation == 'schedule_all':
                print('value fo doctor, clinic, raw_data, request')
                # notification handleed in schedule_by_a_pattern
                schedule_for_everyday(doctor, clinic, raw_data, request)
            else:
                day = WeekDays.objects.get(week_day=raw_data.get("week_day", None))
                if operation == 'toggle_day':
                    # Send notification for booked appt of this particular day
                    toggle_week_day_activation(doctor, clinic, day, appt_queryset)
                if operation == 'toggle_slot':
                    # Send notification if appt is booked
                    appt_id = raw_data.get('appt_id', None)
                    toggle_and_track_appt(appt_queryset, doctor, clinic, day, appt_id)
                
                if operation == 'schedule_day':
                    # send notification to slots which are booked
                    schedule_particular_day(doctor, clinic, day, raw_data, appt_queryset, 'api_request')
                  
        except Exception as e:
            print('value of e in errrororoorororor')
            print(e)
            message = 'fail'
            
        return Response({'message': message}, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)



def toggle_and_track_appt(self, doctor, clinic, day, appt_id):
    is_slot_exist = self.filter(id=appt_id)
    schedule_pattern_object = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic, week_day=day)
    if is_slot_exist.exists() and schedule_pattern_object.exists():
        selected_slot = is_slot_exist.first()
        pattern = schedule_pattern_object.first()
        if selected_slot.active:
            selected_slot.active = False
            
            track_deactivated_slot("deactivate", doctor, clinic, selected_slot.start_appt_time, pattern)
            # now if selected_slot is booked, send the cancelled notification to patient
            if selected_slot.patient:
                selected_slot.patient, selected_slot.relative = None, None
                selected_slot.status = Appointment.ApptStatus.PENDING
                if ApptQrCode.objects.filter(appt_slot=selected_slot).exists():
                    ApptQrCode.objects.filter(appt_slot=selected_slot).delete()
                if selected_slot.status == Appointment.ApptStatus.BOOKED:
                    notification_manager.appt_canceled_by_doctor(selected_slot)
        else:
            selected_slot.active = True
            track_deactivated_slot("activate", doctor, clinic, selected_slot.start_appt_time, pattern)
        selected_slot.save()
    return None

# All Booked Appt List
class BookedApptList(mixins.CreateModelMixin, generics.ListAPIView):
    serializer_class = ser.BookedApptListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        doctor = self.request.user.doctor
        print('INSDIE  of get_queryset')
        # print()
        
        is_only_clinic = self.request.GET.get('is_only_clinic', None)
        # delete the previous booked and pending appts
        try:
            
            
            query_filter = Q(status=Appointment.ApptStatus.BOOKED)
            # create appt in automation form
            if is_only_clinic == 'yes':
                clinic_id = self.request.GET.get('clinic_id', None)
                if clinic_id is not None and clinic_id != '':
                    query_filter.add(Q(clinic__id = clinic_id), Q.AND)
            else:
                Appointment.objects.clear_history()
                schedule_automation(Appointment.objects, doctor, self.request)
                the_day = self.request.GET.get('day', None)
                query_filter.add(Q(day_pattern__week_day__week_day = the_day), Q.AND)
            
            relative_booked_list = doctor.appointment_set.filter(~Q(relative=None) & query_filter
                        ).values('start_appt_time', 'end_appt_time', 'appt_date', 'booked_at').annotate(appt_id=F("id"), patient_id=F("relative__user__id"), clinic_id=F("clinic__id"), patient_name=F("relative__user__full_name"),
                        rtl_patient_name=F("relative__user__rtl_full_name"), patient_phone=F("relative__user__phone"), patient_age=F("relative__user__date_of_birth"), avatar=F("relative__user__avatar"), gender=F("relative__user__gender"), clinic_name=F("clinic__clinic_name"), rtl_clinic_name=F("clinic__rtl_clinic_name"),
                        week_day=F("day_pattern__week_day__week_day"), rtl_week_day=F("day_pattern__week_day__rtl_week_day"),
                        city=F("relative__user__address__city__name"), district=F("relative__user__address__district__name"),
                        rtl_city=F("relative__user__address__city__rtl_name"), rtl_district=F("relative__user__address__district__rtl_name")
                        )
            
            patient_booked_list = doctor.appointment_set.filter(Q(relative=None) & query_filter
                ).values('start_appt_time', 'end_appt_time', 'appt_date', 'booked_at').annotate(appt_id=F("id"), patient_id=F("patient__user__id"), clinic_id=F("clinic__id"), patient_name=F("patient__user__full_name"),
                        rtl_patient_name=F("patient__user__rtl_full_name"), patient_phone=F("patient__user__phone"), patient_age=F("patient__user__date_of_birth"), avatar=F("patient__user__avatar"),  gender=F("patient__user__gender"), clinic_name=F("clinic__clinic_name"), rtl_clinic_name=F("clinic__rtl_clinic_name"),
                        week_day=F("day_pattern__week_day__week_day"), rtl_week_day=F("day_pattern__week_day__rtl_week_day"),
                        city=F("patient__user__address__city__name"), district=F("patient__user__address__district__name"),
                        rtl_city=F("patient__user__address__city__rtl_name"), rtl_district=F("patient__user__address__district__rtl_name")
                        )
            combined_queries = list(itertools.chain(relative_booked_list, patient_booked_list))
        except:
            combined_queries = []
        return combined_queries
    
    def post(self, request, *args, **kwargs):
        # cancel the appt
        # 351_tackle dealt
        raw_data = request.data
        doctor =  self.request.user.doctor
        booked_appt_id = raw_data.get('booked_appt_id')
        message = 'success'
        print('valueof booked_appt_id')
        print(booked_appt_id)
        try:
            
            if booked_appt_id != '' or booked_appt_id is not None:
                raw_appt_object = doctor.appointment_set.filter(id=booked_appt_id)
                if raw_appt_object.exists():
                    notification_manager.appt_canceled_by_doctor(raw_appt_object.first())
                raw_appt_object.update(patient=None, relative=None, status = Appointment.ApptStatus.PENDING)
            else:
                message = 'fail'
        except Exception as e:
            print('value fo Exception')
            print(e)
            message = 'fail'
        return Response({'message': message}, status= status.HTTP_200_OK if message== 'success' else status.HTTP_404_NOT_FOUND)



class MyPatientList(generics.ListAPIView):
    serializer_class = ser.MyPatientListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        try:
            doctor = self.request.user.doctor
            if query is None:
                print('query is none')
                relative_list = doctor.appointment_set.filter(~Q(relative=None) & Q(status=Appointment.ApptStatus.COMPLETED)).values(the_id=F('relative__user'))
                patient_list = doctor.appointment_set.filter(Q(relative=None) & Q(status=Appointment.ApptStatus.COMPLETED)).values(the_id=F('patient__user'))
            else:
                # for Search
                # print('query is not none')
                relative_list = doctor.appointment_set.filter(
                    ~Q(relative=None) & Q(status=Appointment.ApptStatus.BOOKED) & 
                    (Q(relative__user__full_name__icontains=query) | Q(relative__user__rtl_full_name__icontains=query))
                    ).values(the_id=F('relative__user'))
                patient_list = doctor.appointment_set.filter(
                    Q(relative=None) & Q(status=Appointment.ApptStatus.BOOKED) & 
                    (Q(patient__user__full_name__icontains=query) | Q(patient__user__rtl_full_name__icontains=query))
                    ).values(the_id=F('patient__user'))
            # patient id
            patient_id_raw = list(patient_list)
            patient_id_list = [id.get('the_id') for id in patient_id_raw]
            # relative id
            relative_id_raw = list(relative_list)
            relative_id_list = [id.get('the_id') for id in relative_id_raw]
            # get values
            my_patient_list = Patient.objects.filter(user__id__in=patient_id_list)
            
            my_relative_list = Relative.objects.filter(user__id__in=relative_id_list)
            
            combined_query = list(itertools.chain(my_patient_list, my_relative_list))
        except:
            combined_query = []
        return combined_query


class UserPatientDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ser.MyPatientListSerializer
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            patient_id = self.kwargs['id']
            patient_object = Patient.objects.filter(user__id=patient_id)
            serialized = self.get_serializer(patient_object.first()).data
        except Exception as e:
            print('value fo exception')
            print(e)
            serialized = None
        return Response(serialized)


class PatientBookedCompletedAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ser.PatientBookedApptSerialzer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.request.GET.get('user_id')
        query = self.request.GET.get('query')
        # order by appt_date
        try:
            doctor = self.request.user.doctor
            appt_object = doctor.appointment_set
            the_filter = Q(Q(status=Appointment.ApptStatus.COMPLETED) | Q(status=Appointment.ApptStatus.BOOKED))
            user_patient = User.objects.get(id=user_id)
            patient_object = Patient.objects.filter(user__id=user_id)
            if query != 'All':
                formated_time = datetime.strptime(str(query).split(' ')[0], "%Y-%m-%d")
                the_filter.add(Q(Q(appt_date__month=formated_time.month) & Q(appt_date__year=formated_time.year)), Q.AND)
            if patient_object.exists():
                total_completed_appt = appt_object.filter(patient=user_patient.patient, relative=None).order_by('-appt_date').filter(the_filter)
            else:
                total_completed_appt = appt_object.filter(relative=user_patient.relative).order_by('-appt_date').filter(the_filter)
        except Exception as e:
            total_completed_appt = Appointment.objects.none()
        return total_completed_appt

    

class MedicalRecordAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ser.MedicalRecordsSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user_id = self.request.GET.get('user_id')
        query = self.request.GET.get('query')
        print('value fo request.GET')
        print(self.request.GET)
        doctor = self.request.user.doctor
        try:
            the_filter = Q(Q(shared_with = doctor) | Q(related_doctor = doctor))
            user_patient = User.objects.get(id=user_id)
            patient_object = Patient.objects.filter(user__id=user_id)
            if query == 'All':
                filter_query = Q()
            else:
                if query == 'Others':
                    filter_query = Q(~Q(related_doctor=doctor))
                else:
                    filter_query = Q(Q(related_doctor=doctor))
            if patient_object.exists():
                if user_patient.patient.share_record_to_all:
                    the_filter = Q()
                medical_record = MedicalRecords.objects.filter(patient=user_patient.patient, relative=None).filter(the_filter).filter(filter_query).order_by('-updated_at').distinct()
            else:
                if user_patient.relative.share_record_to_all:
                    the_filter = Q()
                medical_record = MedicalRecords.objects.filter(relative=user_patient.relative).filter(the_filter).filter(filter_query).order_by('-updated_at').distinct()
        except Exception as e:
            medical_record = MedicalRecords.objects.none()
        print('value fo medical_record')
        print(len(medical_record))
        return medical_record
    

class ViewDoctorProfile(generics.RetrieveAPIView, mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ser.ViewDoctorProfileSerializer
    lookup_field = 'user'
    # queryset = Doctor.objects.all()
    # queryset = Doctor.objects.filter(professional_status=True)
    
    def retrieve(self, request, *args, **kwargs):
        message = 'success'
        try:
            doctor_id = kwargs['user']
            doctor_object = Doctor.objects.get(user__id=doctor_id, professional_status=True)
            feedback_data = get_feedback_percentage(doctor_object)
            the_data = {
            'doctor_dataset': self.get_serializer(doctor_object, read_only=True).data,
            'feedback_dataset': FeedbackDataSerializer(feedback_data, exclude=('favorite_doctor_list',), read_only=True).data
            }
        except Exception as e:
            the_data = None
            print('value fo  eororororor899898')
            print(e);
            message = 'fail'
        return Response(the_data, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        raw_data = request.data
        print('value of raw_data')
        print(raw_data)
        message = 'success'
        try:
            user = self.request.user
            doctor =  user.doctor
            # update user
            user.full_name = raw_data['name']
            user.rtl_full_name = raw_data['rtl_name']
            user.date_of_birth = raw_data['dob']
            user.gender = raw_data['gender']
            if raw_data['avatar'] != 'no_avatar':
                user.avatar = raw_data['avatar']
            user.save()
            # updte doctor
            is_free_service_acitve = json.loads(raw_data['is_free_service'])
            the_title = DoctorTitle.objects.get(title=raw_data['doctor_title'])
            doctor.doc_license_no = raw_data['license_number']
            doctor.fee = raw_data['fee']
            doctor.is_free_service = is_free_service_acitve
            doctor.title = the_title
            doctor.save()
            # update free service
            if is_free_service_acitve:
                is_free_available = FreeServiceSchedule.objects.filter(doctor=doctor)
                if not is_free_available.exists():
                    FreeServiceSchedule.objects.create(
                        doctor = doctor,
                        start_at = raw_data['free_service_start'],
                        end_at = raw_data['free_service_end']
                    )
        except:
            message = 'fail'
        return Response({'message': 'Success'}, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)

class BasicInfoAPIView(generics.RetrieveAPIView):
    serializer_class = ser.DoctorBasicInfoSerializer
    permisson_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        message = 'success'
        try:
            doctor = request.user.doctor
            free_service_checker(doctor)
            the_data = self.get_serializer(doctor).data
        except Exception as e:
            message = 'fail'
            print('value of e')
            print(e)
            the_data = None
        return Response(the_data, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
        
class CareServiceAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        message = 'success'
        try:
            doctor = self.request.user.doctor
            # all care services
            specialities = Speciality.objects.all()
            conditions = Condition.objects.all()
            services = Service.objects.all()
            # selected care services
            selected_specialities = doctor.speciality.all()
            selected_conditions = doctor.condition.all()
            selected_services = doctor.service.all()
            # 
            all_list= [
                {
                    'speciality_list': specialities, 'condition_list': conditions, 'service_list': services, 
                    'selected_speciality_list': selected_specialities, 'selected_condition_list': selected_conditions, 
                    'selected_service_list': selected_services, 
                } ]
            context = ser.CareServicesSerializer(all_list, many=True).data
        except:
            message = 'fail'
            context = None
        return Response(context, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
    
    
    
    def post(self, request, *args, **kwargs):
        raw_data = request.data
        message = 'success'
        try:
            doctor =  self.request.user.doctor
            professional_profile(raw_data, doctor)
        except:
            message = 'fail'
        return Response({'message': 'Success'}, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
    

class ClinicAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.ClinicSerializer

    def get(self, request, *args, **kwargs):
        message = 'success'
        try:
            query = self.request.GET.get('q')
            doctor = self.request.user.doctor
            if query == 'get_doctor_created_clinic':
                print('value of get_doctor_created_clinic')
                the_filter = Q(created_by=doctor)
            else:
                if query == '' or query is None:
                    the_filter = Q(doctor=doctor)
                else:
                    the_filter = Q(Q(~Q(created_by=doctor) | ~Q(doctor=doctor) ) & (Q(clinic_name__icontains=query) | Q(rtl_clinic_name=query)))
            raw_data = Clinic.objects.filter(the_filter)
        except:
            message = 'fail'
            raw_data = Clinic.objects.none()
        the_data = self.get_serializer(raw_data, many=True).data 
        return Response(the_data, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        raw_data = request.data
        message = 'success'
        new_clinic_id = None
        try:
            doctor =  self.request.user.doctor
            query = self.request.GET.get('q')
            if query == 'pin_coordinate':
                is_clinic_object = Clinic.objects.filter(id=raw_data.get('clinic_id'))
                if is_clinic_object.exists():
                    clinic_object = is_clinic_object.first()
                    clinic_object.latitude = raw_data.get('latitude')
                    clinic_object.longtitude = raw_data.get('longtitude')
                    clinic_object.save()
                    return Response({'message': 'Success'})
                return Response({'message': 'Uknown error occured. Please try again later'}, status=status.HTTP_400_BAD_REQUEST)
            doctor_created_clinic_list_id = list(raw_data.getlist('doctor_created_clinic_list_id'))
            combined_clinic_list = doctor_created_clinic_list_id + list(raw_data.getlist('selected_clinic_list_id'))
            previous_clinics = Clinic.objects.filter(doctor=doctor)
            # Remove Clinic
            for previous_obj in previous_clinics:
                if str(previous_obj.id) not in combined_clinic_list:
                    previous_obj.doctor.remove(doctor)
                    # remove all booked and pending related to this clinic
                    remove_clinic_filter = Q(~Q(status=Appointment.ApptStatus.COMPLETED) & Q(clinic=previous_obj))
                    is_booked_queryset = doctor.appointment_set.filter(status=Appointment.ApptStatus.BOOKED).filter(clinic=previous_obj)
                    # 351_tackle dealt
                    # send notificatin to booked appt
                    if is_booked_queryset.exists():
                        for booked_appt in is_booked_queryset:
                            notification_manager.appt_canceled_by_doctor(booked_appt)
                    doctor.appointment_set.filter(remove_clinic_filter).delete()
                    # delete the day schedule pattern as well
                    DaySchedulePattern.objects.filter(clinic=previous_obj, doctor=doctor).delete()
                    
            # Add
            if len(combined_clinic_list) != 0:
                for clinic_id in combined_clinic_list:
                    clinic_object = Clinic.objects.get(id=clinic_id)
                    clinic_object.doctor.add(doctor)
            # delete created clinics if no doctor is assocated
            previous_created_clinics = Clinic.objects.filter(created_by=doctor).values_list('id', flat=True)
            for existing_id in previous_created_clinics:
                if str(existing_id) not in doctor_created_clinic_list_id:
                    clinic_object_removee = Clinic.objects.get(id=existing_id)
                    # also there is no completed appts as well .. then we can deleted it 
                    is_appt_associated = Appointment.objects.filter(clinic=clinic_object_removee, status=Appointment.ApptStatus.COMPLETED)
                    if clinic_object_removee.doctor.count() == 0 and len(is_appt_associated) == 0:
                        clinic_object_removee.delete()
            if json.loads(raw_data['is_expanded']):
                
                failure_response = Response({'message': "{} is already existed. Please select it instead of adding a new one or change clinic name".format(
                                raw_data['clinic_field_data[clinic_name]']
                            )}, status=status.HTTP_403_FORBIDDEN)
                the_filter = Q(Q(clinic_name__iexact=raw_data['clinic_field_data[clinic_name]']) | 
                            Q(rtl_clinic_name=raw_data['clinic_field_data[rtl_clinic_name]']))
                if raw_data['clinic_field_data[clinic_id]'] != '':
                    is_clinic = Clinic.objects.filter(id=raw_data['clinic_field_data[clinic_id]'])
                    if is_clinic.exists():
                        is_this_name_exist = Clinic.objects.filter(
                            Q(the_filter)
                        ).exclude(id=raw_data['clinic_field_data[clinic_id]'])
                        if is_this_name_exist.exists():
                            print('this is_this_name_exist turel -----')
                            return failure_response
                        # update 
                        new_clinic_id = update_or_save_clinic(doctor, raw_data, is_clinic.first())
                else:
                    is_this_name_exist = Clinic.objects.filter(the_filter)
                    if is_this_name_exist.exists():
                        return failure_response
                    # create
                    new_clinic_id = update_or_save_clinic(doctor, raw_data, None)
        except Exception as e:
            print('value fo error ---')
            print(e)
            message = 'fail'
        return Response({'new_clinic_id': new_clinic_id}, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
    
def update_or_save_clinic(doctor, raw_data, clinic_object=None):
    city_obj = City.objects.get(name=raw_data['clinic_field_data[city_name]'])
    district_obj = District.objects.get(name=raw_data['clinic_field_data[district_name]'], city__name=raw_data['clinic_field_data[city_name]'])
    
    if clinic_object is None:
        new_clinic_obj = Clinic.objects.create(
            clinic_name=raw_data['clinic_field_data[clinic_name]'],
            rtl_clinic_name=raw_data['clinic_field_data[rtl_clinic_name]'],
            address=raw_data['clinic_field_data[address]'],
            rtl_address=raw_data['clinic_field_data[rtl_address]'],
            city=city_obj,
            district=district_obj,
            created_by=doctor,
        )
        new_clinic_obj.doctor.add(doctor)
        new_clinic_obj.refresh_from_db()
        return new_clinic_obj.id
    else:
        clinic_object.clinic_name = raw_data['clinic_field_data[clinic_name]']
        clinic_object.rtl_clinic_name = raw_data['clinic_field_data[rtl_clinic_name]']
        clinic_object.address = raw_data['clinic_field_data[address]']
        clinic_object.rtl_address = raw_data['clinic_field_data[rtl_address]']
        clinic_object.city = city_obj
        clinic_object.district = district_obj
        clinic_object.save()
        clinic_object.refresh_from_db()
        return clinic_object.id


class CityDistrictAPIView(views.APIView):
    def get(self, request):
        city_list = City.objects.all()
        district_list = District.objects.all()
        result_list = [{'city_list': city_list, 'district_list': district_list}]
        serialized_list = ser.CityDistrictListSerializer(result_list, many=True).data
        return Response(serialized_list)


class EducationSubAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        message = 'success'
        try:
            doctor =  self.request.user.doctor
            degree_type_list = DegreeType.objects.all()
            education_degree_list = EducationDegree.objects.all()
            doctor_education_list = doctor.education_set.all()
            the_data = {
                'degree_type_list': ser.DegreeTypeSerializer(degree_type_list, many=True).data,
                'education_degree_list': ser.EducationDegreeSerializer(education_degree_list, many=True).data,
                'doctor_education_list': ser.EducationSerializer(doctor_education_list, many=True).data
            }
        except:
            the_data = {}
            message = 'fail'
        return Response(the_data, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        raw_data = request.data
        message = 'success'
        try:
            doctor =  self.request.user.doctor
            new_education_id = None
            education_list_id = list(raw_data.getlist('education_list_id'))
            temp_previous_educations = Education.objects.filter(doctor=doctor).values_list('id')
            previus_education_id_list = [education_id[0] for education_id in temp_previous_educations]
            # delete those which are not included
            for existing_id in previus_education_id_list:
                if str(existing_id) not in education_list_id:
                    print('value of existing_id')
                    print(existing_id)
                    is_any_associated = Education.objects.get(id=existing_id)
                    is_any_associated.delete()
                
            if json.loads(raw_data['is_editor_expanded']):
                if raw_data['education_field_data[education_id]'] != '':
                    print('it is update  true ====-----')
                    is_education = Education.objects.filter(id=raw_data['education_field_data[education_id]'])
                    if is_education.exists():
                        # update 
                        new_education_id = update_or_save_education(doctor, raw_data, is_education.first())
                else:
                    # create
                    new_education_id = update_or_save_education(doctor, raw_data, None)
        except:
            message = 'fail'
        return Response({'new_education_id': new_education_id}, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)

def update_or_save_education(doctor, raw_data, education_object):
    education_degree = EducationDegree.objects.get(name=raw_data['education_field_data[degree]'], degree_type__name=raw_data['education_field_data[degree_type]'])
    
    if education_object is None:
        new_education_object = Education.objects.create(
            doctor=doctor,
            school_name=raw_data['education_field_data[school_name]'],
            rtl_school_name=raw_data['education_field_data[rtl_school_name]'],
            degree=education_degree,
            start_date=raw_data['education_field_data[start_date]'],
            end_date=raw_data['education_field_data[end_date]'],
        )
        return new_education_object.id
    else:
        education_object.school_name = raw_data['education_field_data[school_name]']
        education_object.rtl_school_name = raw_data['education_field_data[rtl_school_name]']
        education_object.degree = education_degree
        education_object.start_date = raw_data['education_field_data[start_date]']
        education_object.end_date = raw_data['education_field_data[end_date]']
        education_object.save()
        return education_degree.id

class ExperienceAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.ExperienceSerializer

    def get_queryset(self):
        doctor = self.request.user.doctor
        experience_object = doctor.experience_set.all()
        return experience_object

    def post(self, request, *args, **kwargs):
        raw_data = request.data
        doctor =  self.request.user.doctor
        new_experience_id = None
        experience_list_id = list(raw_data.getlist('experience_list_id'))
        
        temp_previous_eperiences = Experience.objects.filter(doctor=doctor).values_list('id')
        previous_experience_id_list = [experience_id[0] for experience_id in temp_previous_eperiences]
        
        # # delete those which are not included
        for existing_id in previous_experience_id_list:
            if str(existing_id) not in experience_list_id:
                is_any_associated = Experience.objects.get(id=existing_id)
                is_any_associated.delete()
            
        if json.loads(raw_data['is_editor_expanded']):
            if raw_data['experience_field_data[experience_id]'] != '':
                is_experience = Experience.objects.filter(id=raw_data['experience_field_data[experience_id]'])
                if is_experience.exists():
                    # update 
                    new_experience_id = update_or_save_experience(doctor, raw_data, is_experience.first())
            else:
                # create
                new_experience_id = update_or_save_experience(doctor, raw_data, None)
        return Response({'new_experience_id': new_experience_id})


def update_or_save_experience(doctor, raw_data, experience_object):
    print('value of dict of raw_data')
    if experience_object is None:
        new_experience_object = Experience.objects.create(
            doctor=doctor,
            hospital_name=raw_data['experience_field_data[hospital_name]'],
            rtl_hospital_name=raw_data['experience_field_data[rtl_hospital_name]'],
            designation=raw_data['experience_field_data[designation]'],
            rtl_designation=raw_data['experience_field_data[rtl_designation]'],
            start_date=raw_data['experience_field_data[start_date]'],
            end_date=raw_data['experience_field_data[end_date]'],
        )
        return new_experience_object.id
    else:
        experience_object.hospital_name = raw_data['experience_field_data[hospital_name]']
        experience_object.rtl_hospital_name = raw_data['experience_field_data[rtl_hospital_name]']
        experience_object.designation = raw_data['experience_field_data[designation]']
        experience_object.rtl_designation = raw_data['experience_field_data[rtl_designation]']
        experience_object.start_date = raw_data['experience_field_data[start_date]']
        experience_object.end_date = raw_data['experience_field_data[end_date]']
        experience_object.save()
        return experience_object.id

class BioAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        doctor = self.request.user.doctor
        the_list= [{'english_bio': doctor.bio, 'farsi_bio': doctor.farsi_bio, 'pashto_bio': doctor.pashto_bio}]
        print('value of the_list')
        print(the_list)
        return Response(the_list)
    
    def post(self, request, *args, **kwargs):
        raw_data = request.data
        doctor =  self.request.user.doctor
        print(raw_data)
        doctor.bio = raw_data['english_bio']
        doctor.farsi_bio = raw_data['farsi_bio']
        doctor.pashto_bio = raw_data['pashto_bio']
        doctor.save()
        return Response({'message': 'Success'})

class AwardAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.AwardSerializer
    
    def get_queryset(self):
        doctor = self.request.user.doctor
        award_object_list = doctor.award_set.all()
        return award_object_list
    
    def post(self, request, *args, **kwargs):
        raw_data = request.data
        new_award_id = None
        doctor =  self.request.user.doctor
        award_list_id = list(raw_data.getlist('award_list_id'))
        
        temp_previous_awards = Award.objects.filter(doctor=doctor).values_list('id')
        previous_award_id_list = [award_id[0] for award_id in temp_previous_awards]
        # # delete those which are not included
        for existing_id in previous_award_id_list:
            if str(existing_id) not in award_list_id:
                is_any_associated = Award.objects.get(id=existing_id)
                is_any_associated.delete()
            
        if json.loads(raw_data['is_editor_expanded']):
            if raw_data['award_field_data[award_id]'] != '':
                is_award = Award.objects.filter(id=raw_data['award_field_data[award_id]'])
                if is_award.exists():
                    # update 
                    new_award_id = update_or_save_award(doctor, raw_data, is_award.first())
            else:
                # create
                new_award_id = update_or_save_award(doctor, raw_data, None)
        return Response({'new_award_id': new_award_id})


def update_or_save_award(doctor, raw_data, award_object):
    if award_object is None:
        new_award_obect = Award.objects.create(
            doctor=doctor,
            award_name=raw_data['award_field_data[award_name]'],
            rtl_award_name=raw_data['award_field_data[rtl_award_name]'],
            award_year=raw_data['award_field_data[award_year]'],
        )
        return new_award_obect.id
    else:
        award_object.award_name = raw_data['award_field_data[award_name]']
        award_object.rtl_award_name = raw_data['award_field_data[rtl_award_name]']
        award_object.award_year = raw_data['award_field_data[award_year]']
        award_object.save()
        return award_object.id
    
    
class FeedbackAPIView(generics.ListAPIView, mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    # we should clear that it should be doctor authentication not normal authentication
    serializer_class = ser.FeedbackSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        try:
            doctor = self.request.user.doctor
            context_queryset = Feedback.objects.filter(appointment__doctor=doctor).filter(~Q(comment='')).order_by('-id')
        except:
            context_queryset = Feedback.objects.none()
        return context_queryset
    
    def post(self, request, *args, **kwargs):
        raw_data = request.data
        message = 'success'
        try:
            user =  self.request.user
            feedback_obj = Feedback.objects.get(id=raw_data['feedback_id'])
            feedback_reply_obj = FeedbackReplies.objects.create(feedback=feedback_obj, author=user, reply=raw_data['reply_text'])
            feedback_reply_obj.refresh_from_db()
        except:
            message = 'fail'
        return Response({'feedback_reply_id': feedback_reply_obj.id}, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
    
class FeedBackDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.FeedbackRepliesSerializer
    lookup_field                = "id"
    queryset = FeedbackReplies.objects.all()

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        the_id = kwargs['id']
        query = self.request.GET.get('q')
        if query is not None or query != '':
            feedback_obj = Feedback.objects.filter(id=query)
            if feedback_obj.exists():
                feedback_obj.delete()
                print('this exisit feedback_obj')
                return Response({'message': 'Feedback has been deleted successfully'})
        return self.destroy(request, *args, **kwargs)
    
class NotificationAPIView(generics.ListAPIView, mixins.CreateModelMixin):
    serializer_class = ser.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    
    
    def get_queryset(self):
        # message = 'success'
        try:
            key = self.request.GET.get("q", None)
            user = self.request.user
            the_filter = Q(receiver=user)
            today_date = date.today()
            three_month_ago = today_date + timedelta(days=90)
            Notification.objects.filter(Q(timestamp__gte=three_month_ago) & ~Q(category=Notification.Categories.review)).delete()
            Notification.objects.filter(seen=False).update(seen=True)
            if key == 'appt_cancelation' or key == 'review':
                # appt_cancelation, review, review_reply
                if key == 'appt_cancelation':
                    the_filter.add(Q(category=key), Q.AND)
                else:
                    the_filter.add(Q(Q(category=key) | Q(category='review_reply')), Q.AND)
                
            if key == 'Clear':
                Notification.objects.filter(the_filter).delete()
                raw_queryset = Notification.objects.none()
            else:
                raw_queryset =  Notification.objects.filter(the_filter).order_by('-timestamp')
            # the_data = self.get_serializer(raw_queryset, many=True).data
        except Exception as e:
            # message = 'fail'
            raw_queryset = Notification.objects.none()
            print('value ro f e')
            print(e)
        # the_queryset = self.get_serializer(raw_queryset, many=True).data
        print('vlue of raw_queryset')
        print(len(raw_queryset))
        print(key)
        return raw_queryset
        # return Response(the_queryset, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        message = 'success'
        data = request.data
        the_dict = dict(request.data)
        field_list = [value[0] for value in the_dict.values()]
        try:
            
            if is_valid_field_with_or(field_list):
                appt_object = Appointment.objects.get(id=data['appt_id'])
                # create notification
                notification_manager.review_created_by_patient(appt_object, data['review'])
                Feedback.objects.create(
                    appointment = appt_object,
                    comment = data['review'],
                    overall_experience = data['overall_experience'],
                    doctor_checkup = data['doctor_checkup'],
                    clinic_environment = data['clinic_environment'],
                    staff_behavior = data['staff_behavior'],
                )
                # delete the notificaiton has been dealt
                if data['note_id'] != '0':
                    print('if conditon is true')
                    Notification.objects.filter(id=data['note_id'], receiver = request.user).delete()
                else:
                    print('execution inside the else ')
                    Notification.objects.filter(appt=appt_object, category=Notification.Categories.review, receiver=request.user).delete()
            else:
                message = 'fail'
        except Exception as e:
            message = 'fail'
        return Response({'message': message})
        


class NotificationDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.NotificationSerializer
    lookup_field                = "id"
    queryset = Notification.objects.all()

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        the_id = kwargs['id']
        try:
            if the_id == '-1' or the_id  == -1:
                note_obj_list = Notification.objects.filter(receiver=self.request.user)
                if note_obj_list.exists():
                    note_obj_list.delete()
                return Response({'message': 'All notifications has been deleted successfully'})
        except:
            pass
        return self.destroy(request, *args, **kwargs)


class ChangePasswordAPIView(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.data['old_pass'] == 'forget_password':
            self.permission_classes = [AnonPermissionOnly]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', None)
        old_pass = request.data.get('old_pass', None)
        new_pass = request.data.get('new_pass', None)
        message = 'success'
        try:
            user =  request.user
            if old_pass == 'forget_password' and not user.is_authenticated:
                forget_user = User.objects.get(phone=phone_number)
                forget_user.set_password(new_pass)
                forget_user.save()
            elif user.is_authenticated:
                if phone_number == user.phone and user.check_password(old_pass):
                    user.set_password(new_pass)
                    user.save()
                else:
                    message = 'no_match'
        except Exception as e:
            message = 'fail'
        return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST if message != 'success' else status.HTTP_200_OK)

class ApptDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ser.ApptDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        message = 'success'
        try:
            doctor = request.user.doctor
            appt_id = kwargs['id']
            appt_object = doctor.appointment_set.get(id=appt_id)
            the_response = self.get_serializer(appt_object).data
        except:
            the_response = None
            messsage = 'fail'
        return Response(the_response, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)


class ProfileSubmissionAPIView(generics.CreateAPIView):
    permission_classses = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        message = 'success'
        message_content = 'The following part of your profile need to be completed:'
        try:
            doctor_id = request.data.get('doctor_id', None)
            operation = request.data.get('operation', None)
            user = request.user
            doctor = user.doctor
            if str(user.id) == doctor_id:
                if operation == 'submit':
                    if not is_valid_field_with_or([user.rtl_full_name, doctor.fee]):
                        message = 'not_completed'
                        message_content += '\n* Basic info is not completed'
                    if doctor.speciality.count() == 0 or doctor.condition.count() == 0 or doctor.service.count() == 0:
                        message = 'not_completed'
                        message_content += '\n* Care Serivces are not completed'
                    clinic_queryset = Clinic.objects.filter(doctor=doctor)
                    if not clinic_queryset.exists():
                        message = 'not_completed'
                        message_content += '\n* Select or register at least one clinic'
                    education_queryset = Education.objects.filter(doctor=doctor)
                    if not education_queryset.exists():
                        message = 'not_completed'
                        message_content += '\n* At least add one education'
                    if not is_valid_field_with_or([doctor.bio, doctor.farsi_bio, doctor.pashto_bio]):
                        message = 'not_completed'
                        message_content += '\n* Biography is not entered in three languages'
                    if message == 'success':
                        doctor.is_profile_on_progress = True
                        doctor.save()
                        
                else:
                    print('now I am requesting ')
                    # puting the profile under review after verification to update
                    doctor.is_profile_on_progress = False
                    doctor.professional_status = False
                    doctor.save()
                    is_booked_queryset = doctor.appointment_set.filter(status=Appointment.ApptStatus.BOOKED)
                    if is_booked_queryset.exists():
                        for booked_appt in is_booked_queryset:
                            notification_manager.appt_canceled_by_doctor(booked_appt)
                    # 351_tackle dealt
                    doctor.appointment_set.filter(~Q(status=Appointment.ApptStatus.COMPLETED)).delete()
                    DaySchedulePattern.objects.filter(doctor=doctor).delete()
                    
                
                doctor.refresh_from_db()
            else:
                message = 'fail'
            
        except Exception as e:
            message = 'fail'
            print('value of e---===---')
            print(e)
        return Response({'message': message, 'message_content': message_content}, status=status.HTTP_400_BAD_REQUEST if message == 'fail' else status.HTTP_200_OK)

# ============== # =====================

# class CursorSetPagination(CursorPagination):
#     page_size = 5
#     page_size_query_param = "page_size"
#     ordering = "-pk"  # '-created' is default

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 35
    max_page_size = 10000
    page_size_query_param = "page_size"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    max_page_size = 1000
    page_size_query_param = "page_size"


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 1000
    page_size_query_param = "page_size"








