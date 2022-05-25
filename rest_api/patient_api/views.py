from django.db.models import fields
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.fields import related
from DoctorPlus.utils import free_service_checker, get_feedback_percentage, is_valid_field_with_or, is_valid_field_with_and
from appointment.views import schedule_automation
from doctor.models import Clinic, Disease, Symptoms
from home.models import Address, City, District
from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework import permissions
import json

from rest_framework import status

# from rest_framework import serializers

from django.db.models import Q
from itertools import chain
from notification import models
from rest_api.utils.pagination import ApptListTilePagination, CustomPagination

# from drf_multiple_model.views import ObjectMultipleModelAPIView

from user.models import (
    BloodGroup, Condition, Relative, Patient, RelativeRelation, Service, Speciality, SpecialityCategory, Doctor
                         )
from rest_framework import mixins, serializers, views
from patient.models import FavoriteDoctor
from appointment.models import Appointment, ApptQrCode, Feedback, FeedbackReplies
from notification.models import Notification
from medicalrecord.models import MedicalRecordFile, MedicalRecords
from notification import notification_manager
from . import serializers as ser
from rest_api.doctor_api.serializers import (
    UserSerializer, ViewDoctorProfileSerializer, ClinicSerializer
    )


from rest_api.user_api.permissins import IsOwnerOrReadOnly
from django.contrib.auth import get_user_model
from django.db.models import F

User = get_user_model()
# from . import permissions as per

# Elbis part start here

class ApptDetailView(generics.RetrieveAPIView, mixins.CreateModelMixin):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.ApptDetailSerializer
    lookup_field                = "id"
    model = Appointment
    # queryset = FeedbackReplies.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        appt_id = self.kwargs['id']
        print('inside the retrieve')
        print(appt_id)
        operation = request.GET.get('operation', None)
        try:
            if operation == 'cancel':
                pass
            else:
                pass
            record_object = Appointment.objects.get(id=appt_id)
            serialized = self.get_serializer(record_object).data
            the_response = Response(serialized, status=status.HTTP_200_OK)
        except Exception as e:
            print('vaue fo e')
            print(e)
            the_response = Response(None, status=status.HTTP_404_NOT_FOUND)
        return the_response
    
    def post(self, request, *args, **kwargs):
        appt_id = self.kwargs['id']
        message = 'success'
        try:
            record_object = Appointment.objects.get(id=appt_id)
            record_object.status = Appointment.ApptStatus.PENDING
            record_object.save()
        except Exception as e:
            message = 'fail'
        return Response({'message': message})


class DoctorApptListView(views.APIView):
    permissions = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        doctor_id = kwargs.get('id', None)
        clinic_id = kwargs.get('clinic_id', None)
        operation = request.GET.get('operation', None)
        patient = request.user.patient
        try:
            the_doctor = Doctor.objects.get(user__id=doctor_id)
            is_all_good = schedule_automation(Appointment.objects, the_doctor, self.request)
            if is_all_good:
                if operation == 'All' or operation is None or operation == '':
                    clinic_queryset = Clinic.objects.filter(doctor=the_doctor)
                    relative_queryset = Relative.objects.filter(patient=patient)
                appt_queryset = Appointment.objects.filter(doctor=the_doctor, clinic__id=clinic_id, active=True, status=Appointment.ApptStatus.PENDING, day_pattern__active=True)
        
                if operation == 'appts':
                    context = {
                        'appts': ser.DoctorApptListSerializer(appt_queryset, many=True).data,
                    }
                else:
                    context = {
                        'patients': ser.RelativeSerializer(relative_queryset, fields=('user',), many=True).data,
                        'clinics': ClinicSerializer(clinic_queryset, fields=('id', 'address', 'district', 'city', 'clinic_name', 'rtl_clinic_name'), many=True).data,
                        'appts': ser.DoctorApptListSerializer(appt_queryset, many=True, read_only=True).data,
                    }
            else:
                if operation == 'appts':
                        context = {
                        'appts': []
                    }
                else:
                    context = {
                        'patients': [],
                        'clinics': [],
                        'appts': [],
                    }
        except Exception as e:
            print('value fo e')
            print(e)
            if operation == 'appts':
                context = {
                    'appts': []
                }
            else:
                context = {
                    'patients': [],
                    'clinics': [],
                    'appts': [],
                }
        
        return Response(context)
    
    def post(self, request, *args, **kwargs):
        message = 'success'
        print('value of equest.data')
        print(request.data)
        print('////////')
        print(kwargs)
        doctor_id = kwargs.get('id', None)
        clinic_id = kwargs.get('clinic_id', None)
        patient_id = request.data.get('patient_id', None)
        slot_id = request.data.get('slot_id', None)
        operation = request.data.get('operation', None)
        patient = request.user.patient
        relative = None
        if not is_valid_field_with_or([patient_id, slot_id, doctor_id, clinic_id, operation]):
            message = 'field_error'
        else:
            patient_id = int(patient_id)
            try:
                is_four_appt = Appointment.objects.filter(patient=patient, status=Appointment.ApptStatus.BOOKED)
                if is_four_appt.count() >= 4 and operation == 'booking':
                    message = 'exceeding_four'
                else:
                    print('valueof message else ')
                    doctor = Doctor.objects.get(user__id=doctor_id)
                    the_filter = Q(Q(patient=patient) & Q(status=Appointment.ApptStatus.BOOKED) & Q(id=slot_id))
                    if request.user.id != patient_id:
                        relative = Relative.objects.get(user__id=patient_id)
                        the_filter.add(Q(relative=relative), Q.AND)
                    else:
                        the_filter.add(Q(relative=None), Q.AND)
                    is_already_booked = doctor.appointment_set.filter(the_filter)
                    if is_already_booked.exists() and operation == 'booking':
                        message = 'already_booked'
                    else:
                        if operation == 'reschedule' or operation == 'cancel':
                            is_already_booked.update(patient=None, relative=None, status = Appointment.ApptStatus.PENDING)
                            if operation == 'cancel':
                                notification_manager.appt_cancel_by_patient(is_already_booked.first())
                                ApptQrCode.objects.filter(appt_slot=is_already_booked.first()).delete()
                        if operation == 'reschedule' or operation == 'booking':
                            appt_object = doctor.appointment_set.get(id=slot_id)
                            appt_object.patient = patient
                            appt_object.relative = relative
                            appt_object.status = Appointment.ApptStatus.BOOKED
                            appt_object.save()
                            # create qr code 
                            ApptQrCode.objects.update_or_create(appt_slot=appt_object)
            except Exception as e:
                print('value of e ------')
                print(e)
                message = 'fail'
        return Response({'message': message})


def patient_appt_analytic(patient_user, is_patient=True):
    last_completed_appt = None
    total_booked_appt = 0
    family_member_no = 0
    medical_record_no = 0
    share_to_all = False
    blood_group = None
    the_filter = Q(status=Appointment.ApptStatus.COMPLETED)
    if is_patient:
        share_to_all = patient_user.patient.share_record_to_all
        blood_group = patient_user.patient.blood_group
        the_filter.add(Q(patient__user__id=patient_user.id, relative=None), Q.AND)
    else:
        share_to_all = patient_user.relative.share_record_to_all
        blood_group = patient_user.relative.blood_group
        the_filter.add(Q(relative__user__id=patient_user.id), Q.AND)

    appt_queryset = Appointment.objects.filter(the_filter).order_by('-appt_date')
    if appt_queryset.exists():
        last_completed_appt = appt_queryset.first().appt_date or None
        total_booked_appt = appt_queryset.count() or 0

    if is_patient:
        family_member_no = Relative.objects.filter(patient=patient_user.patient).count() or 0
    if is_patient:
        medical_record_no = MedicalRecords.objects.filter(Q(patient=patient_user.patient) & Q(relative=None)).count() or 0
    else:
        medical_record_no = MedicalRecords.objects.filter(relative=patient_user.relative).count() or 0

    return last_completed_appt, total_booked_appt, family_member_no, medical_record_no, share_to_all, blood_group


class ViewPatientOrRelativeProfileView(views.APIView):
    permissions = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        patient_user = request.user
        print('value of patient_user')
        # patient = patient_user.patient
        # query = request.GET.get('q', None)
        is_patient = True
        user_id = int(kwargs.get('id', None))
        try:
            if patient_user.id != user_id:
                is_patient = False
                patient_user = User.objects.get(id=user_id)
            func_result = patient_appt_analytic(patient_user, is_patient)
            patient_dict = {
                'user': patient_user,
                'last_completed_appt': func_result[0],
                'total_booked_appt': func_result[1],
                'family_member_no': func_result[2],
                'medical_record_no': func_result[3],
                'share_record_to_all': func_result[4],
                'blood_group': func_result[5],
            }
            context = ser.PatientSerializer(patient_dict, read_only=True).data
            # get appt_list
            
            # the_appts = get_appt_by_query(query, patient_user, not is_patient, True)
            # appt_list = ser.ApptListTileSerializer(the_appts, many=True, fields=(
            #     'id', 'status', 'start_appt_time', 'end_appt_time', 'feedback_status', 'appt_date', 'doctor', 'clinic')).data
            # record_list = get_records_by_query(query, patient_user, not is_patient)
            # medical_record_list = ser.MedicalRecordTileSerializer(record_list, many=True, fields=('id', 'related_doctor', 'record_file_no', 'title')).data
          
            # context = {
            #     'patient': patient_data,
            #     'appt_list': appt_list,
            #     'medical_record_list': medical_record_list,
            # }
        except Exception as e:
            print('value of e')
            print(e)
            context = None
            # context = {
            #     'patient': None,
            #     'appt_list': [],
            #     'medical_record_list': [],
            # }
        return Response(context)


class MedicalRecordTileView(mixins.CreateModelMixin, generics.ListAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = ser.MedicalRecordTileSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        try:
            patient_user = self.request.user
            query = self.request.GET.get('q', None)
            print('value of self.request.GET')
            print(self.request.GET)
            is_profile = self.request.GET.get('is_profile', None)
            if is_profile == 'no':
                print('length of the insid ethe no item')
                the_records = get_records_by_query(query, patient_user)
                print(the_records)
            else:
                # new part for both patient and relative
                the_id = self.request.GET.get('user_id', None)
                is_patient = True
                user_id = int(the_id)
                if patient_user.id != user_id:
                    is_patient = False
                    patient_user = User.objects.get(id=user_id)
                the_records = get_records_by_query(query, patient_user, not is_patient)
        except:
            the_records = MedicalRecords.objects.none()
        print('length of the the_records')
        print(the_records)
        return the_records


def get_records_by_query(query, patient_user, is_relative=False):
    if query == 'Booked' or query == 'Completed':
        query = ''
    if is_relative:
        patient = patient_user.relative
    else:
        patient = patient_user.patient
    try:
        if not is_relative:
            the_filter = Q(patient=patient)
            if query == '' or query is None or query == 'All':
                the_records = MedicalRecords.objects.filter(the_filter).order_by('-updated_at')
            elif query == 'Me':
                the_records = MedicalRecords.objects.filter(Q(relative=None) & the_filter).order_by('-updated_at')
                
            elif query == 'Relatives':
                the_records = MedicalRecords.objects.filter(~Q(relative=None) & the_filter).order_by('-updated_at')
            else:
                the_filter.add(Q(Q(relative__user__full_name__icontains=query) | Q(relative__user__rtl_full_name__contains=query)), Q.AND)
                the_records = MedicalRecords.objects.filter(the_filter).order_by('-updated_at').distinct()
        else:
            the_records = MedicalRecords.objects.filter(relative=patient).order_by('-updated_at').distinct()
          
    except Exception as e:
        print('value fo e in eroror ror ro r')
        print(e)
        the_records = MedicalRecords.objects.none()
    return the_records



class MedicalRecordDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.MedicalRecordDetailSerializer
    lookup_field                = "id"
    model = MedicalRecords
    # queryset = FeedbackReplies.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        record_id = self.kwargs['id']
        try:
            record_object = MedicalRecords.objects.get(id=record_id)
            serialized = self.get_serializer(record_object).data
            the_response = Response(serialized, status=status.HTTP_200_OK)
        except Exception as e:
            print('vaue fo e')
            print(e)
            the_response = Response(None, status=status.HTTP_404_NOT_FOUND)
        return the_response

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        the_id = kwargs['id']
        message = 'success'
        try:
            self.model.objects.filter(id=the_id).delete()
        except:
            message = 'fail'
        return Response({'message': message})
        # return self.destroy(request, *args, **kwargs)

class MedicalReocrdShareHander(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        the_response = 'success'
        record_id = request.data.get('record_id', None)
        doctor_id = request.data.get('doctor_id', None)
        operation = request.data.get('operation', None)
        try:
            doctor = Doctor.objects.get(user__id=doctor_id)
            record = MedicalRecords.objects.get(id=record_id)
            if operation == 'remove':
                record.shared_with.remove(doctor)
            else:
                record.shared_with.add(doctor) 
        except:
            the_response = 'fail'
        return Response({'message': the_response})


class MedicalReocrdGeneralShareHander(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        the_response = 'success'
        record_id = request.data.get('record_id', None)
        the_bool = request.data.get('the_bool', None)
        try:
            record = MedicalRecords.objects.get(id=record_id)
            record.general_access = json.loads(the_bool)
            record.save()
        except Exception as e:
            the_response = 'fail'
        return Response({'message': the_response})


class CreateMedicalRecordDataView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        patient = request.user.patient
        the_filter = Q(Q(status=Appointment.ApptStatus.COMPLETED) | Q(status=Appointment.ApptStatus.BOOKED))
        try:
            doctor_id_collection = patient.appointment_set.filter(the_filter).values_list('doctor__user__id', flat=True).distinct()
            doctor_queryset = User.objects.filter(id__in=doctor_id_collection)
            relative_queryset = Relative.objects.filter(patient=patient)
          
            the_response = ser.CreateMedicalReocrdDataSerializer({'my_relatives': relative_queryset, 'my_doctors': doctor_queryset}, read_only=True).data
        except Exception as e:
            print('value fo e ====')
            print(e)
            the_response = ser.CreateMedicalReocrdDataSerializer({'my_relatives': [], 'my_doctors': []}, read_only=True).data
        return Response(the_response)
    
    def post(self, request, *args, **kwargs):
        the_message = 'success'
        data = request.data
        print('value fo data')
        print(data)
        patient = request.user.patient
        try:
            if data['patient'] == 'Me':
                relative = None
            else:
                relative_filter = Q(Q(user__full_name=data.get('patient', None)) | Q(user__rtl_full_name=data.get('patient', None)))
                relative = Relative.objects.filter(relative_filter).distinct().first()
            related_doctor = Doctor.objects.get(user__id=data.get('related_doctor', None))
            general_access = json.loads(data['is_shared_to_all'])
            shared_with = data.getlist('shared_with', None)
            files = data.getlist('file', None)
            title = data.get('title', None)
            if data.get('operation', None) == 'create':
                record_object = MedicalRecords.objects.create(
                    patient=patient, relative=relative, related_doctor=related_doctor, 
                    title=title, general_access=general_access
                )
                if len(shared_with) != 0:
                    shared_with_doctors = Doctor.objects.filter(user__id__in=shared_with)
                    record_object.shared_with.add(*shared_with_doctors)
                if len(files) != 0:
                    for file in files:
                        MedicalRecordFile(medical_record=record_object, file=file).save()
            else:
                print('isndie the edit_record of else')
                edit_record(data, patient, relative, related_doctor, general_access, shared_with, files, title)
            
        except Exception as e:
            the_message = 'fail'
            print('value of e')
            print(e)
        return Response({'message': the_message})

def edit_record(data, patient, relative, related_doctor, general_access, shared_with, files, title):
    record_id = data.get('record_id', None)
    removed_files_id = data.getlist('removed_files', None)
    record_object = MedicalRecords.objects.get(id=record_id)
    new_related_doctor = related_doctor if record_object.related_doctor != related_doctor else record_object.related_doctor
    record_object.title = title
    record_object.patient = patient
    record_object.relative = relative
    record_object.general_access = general_access
    record_object.related_doctor = new_related_doctor
    record_object.save()
    if len(removed_files_id) != 0:
        MedicalRecordFile.objects.filter(id__in=removed_files_id).delete()
    if len(shared_with) != 0:
        record_object.shared_with.clear()
        shared_with_doctors = Doctor.objects.filter(user__id__in=shared_with)
        record_object.shared_with.add(*shared_with_doctors)
        record_object.shared_with.add(new_related_doctor)
    else:
        record_object.shared_with.clear()
        record_object.shared_with.add(new_related_doctor)
    
    if len(files) != 0:
        for file in files:
            MedicalRecordFile(medical_record=record_object, file=file).save()
    


class FavoriteDoctorListView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.DoctorListTileSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        try:
            patient = self.request.user.patient
            favoite_list = Doctor.objects.filter(favoritedoctor__patient=patient, professional_status=True)
        except:
            favoite_list = Doctor.objects.none()
        return favoite_list

    def post(self, request, *args, **kwargs):
        doctor_id = request.data.get('doctor_id', None)
        operation = request.data.get('operation', None)
        message = 'added_successfully'
        if doctor_id != '' and doctor_id is not None:
            try:
                patient =  self.request.user.patient
                favoite_doctors = FavoriteDoctor.objects.get(patient=patient)
                doctor = Doctor.objects.get(user__id=doctor_id)
                if operation == 'add':
                    favoite_doctors.doctor.add(doctor)
                else:
                    favoite_doctors.doctor.remove(doctor)
                    message = 'removed_successfully'
            except Exception as e:
                print('value of error ')
                print(e)
                message = 'failed'
        return Response({'message': message})

class RelativeTileView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ser.RelativeTileSerializer
    
    def get_queryset(self):
        try:
            patient = self.request.user.patient
            relative_list = Relative.objects.filter(patient=patient).order_by('-user__id')
        except:
            relative_list = Relative.objects.none()
        return relative_list
    
    def post(self, request, *args, **kwargs):
        the_response = 'success'
        patient = request.user.patient
        print('value fo request')
        print(request.data)
        operation = request.data.get('operation', None)
        the_id = request.data.get('id', None)
        name = request.data.get('name', None)
        rtl_name = request.data.get('rtl_name', None)
        city_id = request.data.get('city_id', None)
        district_id = request.data.get('district_id', None)
        dob = request.data.get('dob', None)
        blood_group = request.data.get('blood_group', None)
        gender = request.data.get('gender', None)
        phone_number = request.data.get('phone_number', None)
        relation_id = request.data.get('relation_id', None)
        avatar = request.data.get('avatar', None)
        user_id = None
        the_avatar = None
        try:
            if operation == 'create' or operation == 'update':
                city = City.objects.get(id=city_id)
                district = District.objects.get(id=district_id)
                the_relation = RelativeRelation.objects.get(id=relation_id)
                the_blood = BloodGroup.objects.get(name=blood_group)
                is_any = User.objects.filter(phone=phone_number)
                is_shared_to_all = json.loads(request.data.get('is_shared_to_all', None))
                same_name_filter = Q(Q(Q(user__full_name=name) | Q(user__rtl_full_name=rtl_name)) & Q(patient=patient))
                if operation == 'update':
                    same_name_filter.add(~Q(user__id=the_id), Q.AND)
                is_same_name = Relative.objects.filter(same_name_filter)
                
            # create
            if operation == 'create':
                if not is_any.exists():
                    new_avatar = None
                    if avatar != 'no_avatar':
                        new_avatar = avatar
                    if not is_same_name.exists():
                        user = User.objects.create(
                        full_name=name, rtl_full_name=rtl_name, date_of_birth=dob, avatar=new_avatar,
                        gender=gender, phone=phone_number, user_type='Relative', active=True)
                        user.save()
                        user.refresh_from_db()
                        user_id = user.id
                        try:
                            the_avatar = user.avatar.url
                        except Exception as e:
                            pass
                        # create relative
                        Relative.objects.create(
                            user = user, patient=patient, blood_group=the_blood, 
                            relation=the_relation, share_record_to_all=is_shared_to_all
                        )
                        # address
                        Address.objects.create(user=user, city=city, district=district)
                    else:
                        the_response = 'same_name'
                else:
                    the_response = 'phone'
            # update
            
            if operation == 'update':
                is_same=User.objects.filter(phone=phone_number)
                if not is_same_name.exists():
                    if len(is_same) == 1 or len(is_any) == 0:
                        relative_user = User.objects.get(id=the_id)
                        relative_user.full_name = name
                        relative_user.rtl_full_name = rtl_name
                        relative_user.dob = dob
                        relative_user.date_of_birth = dob
                        relative_user.gender = gender
                        if avatar != 'no_avatar':
                            relative_user.avatar = avatar
                        relative_user.phone = phone_number
                        relative_user.save()
                        relative_user.refresh_from_db()
                        
                        try:
                            the_avatar = relative_user.avatar.url
                        except Exception as e:
                            pass
                        # address
                        address = relative_user.address
                        address.city = city
                        address.district = district
                        address.save()
                        # relative
                        relative = relative_user.relative
                        relative.blood_group = the_blood
                        relative.relation = the_relation
                        relative.share_record_to_all = is_shared_to_all
                        relative.save()
                        
                    else:
                        the_response = 'phone'
                else:
                    the_response = 'same_name'
            if operation == 'delete':
                try:
                    User.objects.get(id=the_id).delete()
                    print('inside the delete section')
                except Exception as e:
                    print('value of e')
                    print(e)
                    the_response = 'fail'
            
            
        except Exception as e:
            the_response = 'fail'
            print('value fo e')
            print(e)
        print('value of final result ')
        print(the_avatar)
        print(the_response)
        return Response({'message': the_response, 'avatar': the_avatar, 'id': user_id})

class ApptListTileView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes       = [permissions.IsAuthenticated]
    serializer_class         = ser.ApptListTileSerializer
    pagination_class = ApptListTilePagination

    def get_queryset(self):
        print('inside the get_queryset')
        print(self.request.GET)
        is_profile = self.request.GET.get('is_profile', None)
        try:
            patient_user = self.request.user
            query = self.request.GET.get('q', None)
            if is_profile == 'no':
                if query == '' or query == 'All':
                    Appointment.objects.clear_history()
                appts = get_appt_by_query(query, patient_user)
            else:
                # to view by profile
                the_id = self.request.GET.get('user_id', None)
                is_patient = True
                user_id = int(the_id)
                if patient_user.id != user_id:
                    is_patient = False
                    patient_user = User.objects.get(id=user_id)
                print('valur of is_patient')
                print(is_patient)
                print(patient_user.id)
                print(user_id)
                appts = get_appt_by_query(query, patient_user, not is_patient, True)
        except Exception as e:
            print('value of user_id')
            print(e)
            appts = Appointment.objects.none()
        print('value fo apptsthe appt lenth ')
        print(len(appts))
        return appts

    def post(self, request, *args, **kwargs):
        raw_data = request.data
        print('value fo raw_data')
        print(raw_data)
        appt_id = raw_data.get('appt_id', None)
        message = 'success'
        try:
            patient =  self.request.user.patient
            the_appt_raw = Appointment.objects.filter(id=appt_id, patient=patient)
            if the_appt_raw.exists():
                the_appt = the_appt_raw.first()
                the_appt.status = Appointment.ApptStatus.COMPLETED
                the_appt.save()
                # create request for patient to leave feedback
                notification_manager.review_requested_from_patient(the_appt)
                # add the doctor to favorite list
                favorite_docs = FavoriteDoctor.objects.filter(patient=patient, doctor=the_appt.doctor)
                if not favorite_docs.exists():
                    patient.favoritedoctor.doctor.add(the_appt.doctor)
            else:
                message = 'not_yours'
        except Exception as e:
            message = 'fail'
        return Response({'message': message})


def get_appt_by_query(query, patient_user, is_relative=False, is_view_profile=False):
    
    if is_relative:
        patient = patient_user.relative
    else:
        patient = patient_user.patient
    if query == 'Booked' or query == 'Completed':
        the_status = Appointment.ApptStatus.BOOKED if query == 'Booked' else Appointment.ApptStatus.COMPLETED
        the_filter = Q(Q(status=the_status) & Q(active=True))
    else:
        the_filter = Q(Q(status=Appointment.ApptStatus.BOOKED) | Q(status=Appointment.ApptStatus.COMPLETED))
    try:
        
        if not is_relative:
            the_filter.add(Q(patient=patient), Q.AND)
           
            if query == 'Me' or query == 'Booked' or query == 'Completed':
                if is_view_profile:
                    the_filter.add(Q(relative=None), Q.AND)
            if query == '' or query is None or query == 'All':
                appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()
            elif query == 'Me':
                print('valuer of the_filter')
                print(the_filter)
                the_filter.add(Q(relative=None), Q.AND)
                appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()
            elif query == 'Booked':
                print('valuer of the_filter')
                print(the_filter)
                appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()
            elif query == 'Completed':
                appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()
            elif query == 'Relatives':
                # all relatives
                appts = Appointment.objects.filter(the_filter).filter(~Q(relative=None)).order_by('status', '-booked_at').distinct()
            else:
                print('other other other other')
                the_filter.add(Q(Q(relative__user__full_name__icontains=query) | Q(relative__user__rtl_full_name__contains=query)), Q.AND)
                appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()
        else:
            the_filter.add(Q(relative=patient), Q.AND)
            if query != '' and query is not None:
                if query == 'All':
                    appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()
                if query == 'Booked':
                    appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()
                elif query == 'Completed':
                    appts = Appointment.objects.filter(the_filter).order_by('status', '-booked_at').distinct()   
            else:
                appts = Appointment.objects.none()
    except:
        appts = Appointment.objects.none()
    print('lenght of appts')
    print(len(appts))
    return appts

class ViewDoctorProfileDetail(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user', None)
        patient_user = request.user.patient
        message = 'success'
        try:
            id_list = FavoriteDoctor.objects.filter(patient=patient_user).values_list('doctor__user__id', flat=True)
            doctor_object = Doctor.objects.get(user__id=user_id)
            free_service_checker(doctor_object)
            feedback_data = get_feedback_percentage(doctor_object)
            feedback_data['favorite_doctor_list'] = list(id_list)
            the_doctor = ViewDoctorProfileSerializer(doctor_object, read_only=True).data
            is_there_completed_appt = doctor_object.appointment_set.filter(patient=patient_user, status=Appointment.ApptStatus.COMPLETED)
            is_completed_appt_there = False
            if is_there_completed_appt.exists():
                is_completed_appt_there = True
            context = {
                'is_completed_appt_there': is_completed_appt_there,
                'doctor_object': the_doctor,
                'feedback_data': ser.FeedbackDataSerializer(feedback_data, read_only=True).data,
            }
        except Exception as e:
            print(e)
            context = None
            message = 'fail'
        return Response(context, status=status.HTTP_200_OK if message == 'success' else status.HTTP_400_BAD_REQUEST)

from django.db.models import Count

class FindDoctorDataView(views.APIView):
    
    def get(self, request, *args, **kwargs):
        print('inside the get')
        context = None
        try:
            # the_filter = Q(professional_status=True)
            # top_doctors = Doctor.objects.filter(the_filter)[:10]
            print('value fo top_doctors1')
            # print(top_doctors1)
            # if request.user.is_authenticated:
            #     print('user is authenticated')
                # get top five from user city and top from the rest of cities except from his city
                
            # criteria:
            # more reviews, more experience, and more completed appts
            top_doctors = Doctor.objects.filter(professional_status=True).annotate(
                num_appts=Count('appointment', filter=Q(appointment__status=Appointment.ApptStatus.COMPLETED))
                ).order_by('-num_appts')[:10]
            # print('value of top_doctors')
            # print(top_doctors)
            speciality_categories = SpecialityCategory.objects.all()
            the_list = [{
                'speciality_categories': speciality_categories,
                'top_doctors': top_doctors
            }]
            context = ser.FindDoctorDataSerializer(the_list, many=True).data
        except Exception as e:
            context = ser.FindDoctorDataSerializer([], many=True).data
            print('value of e')
            print(e)
        return Response(context)

# class SearchDoctorView(views.APIView):
class SearchDoctorView(generics.ListAPIView):
    pagination_class = CustomPagination
    serializer_class = ser.DoctorListTileSerializer
         
    def search_doctor_detail_by_query(self, query):
        search_doctor_details = Q(
            Q(user__full_name__icontains=query)
            | Q(user__rtl_full_name__icontains=query)
            # below are unnecessary parameters that make search slow
            # | Q(user__email__icontains=query)
            # | Q(bio__icontains=query)
            # | Q(farsi_bio__icontains=query)
            # | Q(pashto_bio__icontains=query)
            # | Q(title__title__icontains=query)
            # | Q(title__farsi_title__contains=query)
            # | Q(title__pashto_title__contains=query)
        )
        return search_doctor_details
    
    def search_speciality_by_query(self, query):
        search_speciality = (
            Speciality.objects.filter(
                Q(name__icontains=query)
                | Q(farsi_name__contains=query)
                | Q(pashto_name__contains=query)
                | Q(speciality_category__name__icontains=query)
                | Q(speciality_category__farsi_name__contains=query)
                | Q(speciality_category__pashto_name__contains=query)
                | self.search_disease_by_query(query)
            ).values('id').distinct()
        )
        return Q(speciality__in=search_speciality) 
    
    def search_condition_by_query(self, query):
        search_condition = (
            Condition.objects.filter(
                Q(name__icontains=query)
                | Q(farsi_name__contains=query)
                | Q(pashto_name__contains=query)
            ).values('id').distinct()
        )
        return Q(condition__in=search_condition)
    
    def search_service_by_query(self, query):
        search_service = (
            Service.objects.filter(
                Q(name__icontains=query)
                | Q(farsi_name__contains=query)
                | Q(pashto_name__contains=query)
            ).values('id').distinct()
        )
        return Q(service__in=search_service)
    
    def search_disease_by_query(self, query):
        search_disease = (
            Disease.objects.filter(
                Q(name__icontains=query) | Q(farsi_name__contains=query) | Q(pashto_name__contains=query) 
                | self.search_symptom_by_query(query)
            ).values("id").distinct()
        )
        return Q(disease__in=search_disease)
    
    def search_symptom_by_query(self, query):
        search_symptom = (
            Symptoms.objects.filter(
                Q(name__icontains=query)
                |Q(farsi_name__contains=query) 
                |Q(pashto_name__contains=query)).values("id").distinct()
        )
        return Q(symptom__in=search_symptom)
    
    def search_clinic_by_query(self, query):
        search_clinic = Q(
                Q(clinic__clinic_name__icontains=query) 
                | Q(clinic__rtl_clinic_name__icontains=query)
        )
        return search_clinic
    
    def the_search(self, the_data):
        query = the_data.get('query', None)
        province = the_data.get('province', None)
        speciality = the_data.get('speciality', None)
        main_filter = Q()
        if query != '' and query is not None:
            doctor_basic_detail = self.search_doctor_detail_by_query(query)
            speciality_relation = self.search_speciality_by_query(query)
            condition_relation = self.search_condition_by_query(query)
            service_relation = self.search_service_by_query(query)
            search_clinic = self.search_clinic_by_query(query)
            
            main_filter = main_filter.add(Q(
                doctor_basic_detail
                | speciality_relation
                | condition_relation
                | service_relation
                | search_clinic
                ), Q.AND)
            
        if speciality != '' and speciality is not None:
            search_by_speciality = Q(
                Q(speciality__speciality_category__name__icontains=speciality)
                | Q(speciality__speciality_category__farsi_name__contains=speciality)
                | Q(speciality__speciality_category__pashto_name__contains=speciality)
                | Q(speciality__name__contains=speciality)
                | Q(speciality__farsi_name__contains=speciality)
                | Q(speciality__pashto_name__contains=speciality)
            )
            main_filter.add(search_by_speciality, Q.AND)
            
        
        if province != '' and province is not None:
            search_by_province = Q(
                Q(clinic__city__name__icontains=province) 
                | Q(clinic__city__rtl_name__icontains=province)
             )
            main_filter.add(search_by_province, Q.AND)
                

        if is_valid_field_with_and([query, province, speciality]):
            result_list = Doctor.objects.none()
        else:
            result_list = Doctor.objects.filter(main_filter).filter(professional_status=True).distinct()
        return result_list
    
    def get_queryset(self):
        print('inside the get')
        context = None
        try:
            the_queryset = self.the_search(self.request.GET)
            # the_queryset = Doctor.objects.all()
            # context = ser.DoctorListTileSerializer(the_queryset, many=True).data
            print('the real context will be executed')
        except Exception as e:
            print('the value of error')
            print(e)
            # maybe i should get the top doctors here
            
        return the_queryset
        # return Response(context)


class PatientProfileSettingView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        the_patient = request.user.patient or None
        the_data = ser.PatientProfileSettingSerializer(the_patient).data
        return Response(the_data)
    
    def post(self, request, *args, **kwargs):
        the_response = 'success'
        print('value fo request.data--===----')
        print(request.data)
        user = request.user
        name = request.data.get('name', None)
        rtl_name = request.data.get('rtl_name', None)
        city_id = request.data.get('city_id', None)
        district_id = request.data.get('district_id', None)
        dob = request.data.get('dob', None)
        blood_group = request.data.get('blood_group', None)
        gender = request.data.get('gender', None)
        avatar = request.data.get('avatar', None)
        is_shared_to_all = json.loads(request.data.get('is_shared_to_all', None))
        avatar_url = None
        try:
            user.full_name = name
            user.rtl_full_name = rtl_name
            user.date_of_birth = dob
            user.gender = gender
            if avatar != 'no_avatar':
                user.avatar = avatar
            user.save()
            user.refresh_from_db()
            # patient
            patient = user.patient
            the_blood = BloodGroup.objects.get(name=blood_group)
            patient.blood_group = the_blood
            patient.share_record_to_all = is_shared_to_all
            patient.save()
            # address
            city = City.objects.get(id=city_id)
            district = District.objects.get(id=district_id)
            address = user.address
            address.city = city
            address.district = district
            address.save()
            # get avatar
            try:
                avatar_url = user.avatar.url
            except:
                avatar_url = None
        except Exception as e:
            the_response = 'fail'
            print('value fo e')
            avatar_url = None
            print(e)
        return Response({'message': the_response, 'avatar': avatar_url}, status=status.HTTP_200_OK if the_response == 'success' else status.HTTP_400_BAD_REQUEST)


class DistrictByCityView(generics.ListAPIView):
    serializer_class = ser.DistrictSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        city_id = self.request.GET.get('q', None)
        district_list = District.objects.filter(city__id=city_id)
        return district_list


class RelativeRelationView(generics.ListAPIView):
    serializer_class = ser.RelativeRelationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RelativeRelation.objects.all()


class UpdateRelativeInitialDataView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # relative_id = request.data.get('relative_id', None)
        relative_id = request.GET.get('the_id', None)
        print('value of relative_id')
        print(relative_id)
        try:
            user = User.objects.get(id=relative_id)
            relative_relation_queryset = RelativeRelation.objects.all()
            city = user.address.city.name
            district_queryset = District.objects.filter(city__name=city)
            queryset = {
                'relative_relation_list': ser.RelativeRelationSerializer(relative_relation_queryset, many=True).data,
                'blood_group': user.relative.blood_group.name,
                'city': city,
                'district': user.address.district.name,
                'phone': user.phone,
                'dob': user.date_of_birth,
                'district_list': ser.DistrictSerializer(district_queryset, many=True).data,
            }
            # the_data = ser.UpdateRelativeInitialDataSerializer(queryset, read_only=True).data
        except Exception as e:
            queryset = {}
            print('valeu fo e')
            print(e)
        return Response(queryset)
