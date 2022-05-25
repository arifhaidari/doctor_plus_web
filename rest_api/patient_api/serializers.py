from importlib.abc import ExecutionLoader
from operator import truediv
from pickletools import read_long1
from django.db.models import fields
from django.db.models.fields import files
from django.template.defaultfilters import title
from DoctorPlus.utils import star_out_of_five
from rest_framework import serializers
from django.db.models import Q
from drf_writable_nested.serializers import WritableNestedModelSerializer


from user import validators as user_valid
from home.models import Address, District
# from notification import notification_manager, patient_notifications
from notification.models import Notification
from user.models import Doctor, Relative, RelativeRelation, SpecialityCategory, User, Patient
from patient.models import FavoriteDoctor
from appointment.models import Appointment, ApptConditionTreat, Feedback, FeedbackReplies
from medicalrecord.models import MedicalRecordFile, MedicalRecords

# from .doctor_api.serializers import UserSerializer
# from ..doctor_api.serializers import UserSerializer
from rest_api.doctor_api.serializers import (
    ClinicSerializer, DistrictSerializer, UserSerializer, SpecialitySerializer, DoctorTitleSerializer,
     ClinicSerializer, DaySchedulePatternSerializer
    )

def dynamic_fields(self, args, kwargs):
    fields = kwargs.pop("fields", None)
    exclude = kwargs.pop("exclude", None)
    super(self.__class__, self).__init__(*args, **kwargs)
    # setting fields dynamically
    fields and [self.fields.pop(field_name) for field_name in set(self.fields) - set(fields)]
    exclude and [self.fields.pop(field_name) for field_name in set(self.fields) if field_name in set(exclude)]


# Eblis part start

class RelativeRelationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RelativeRelation
        fields = '__all__'

class RelativeTileSerializer(serializers.ModelSerializer):
    user = UserSerializer(fields=('id', 'full_name', 'rtl_full_name', 'avatar', 'gender'))
    relation = RelativeRelationSerializer(read_only=True)
    class Meta:
        model = Relative
        fields = 'user', 'relation', 'share_record_to_all'

class DoctorListTileSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    user = UserSerializer(read_only=True, fields=("id", "full_name", "rtl_full_name", 'gender', "avatar"))
    clinic_list = serializers.SerializerMethodField(read_only=True)
    speciality_list = serializers.SerializerMethodField(read_only=True)
    title = DoctorTitleSerializer(read_only=True)
    review_no = serializers.SerializerMethodField(read_only=True)
    average_star = serializers.SerializerMethodField(read_only=True)
    
    def get_speciality_list(self, instance):
        specialities = instance.speciality.all()[:2]
        return SpecialitySerializer(specialities, many=True).data
    
    def get_clinic_list(self, instance):
        clinic_queryset = instance.clinic_set.all()[:1]
        return ClinicSerializer(clinic_queryset, many=True, exclude=('latitude', 'longtitude', 'active', 'created_at', 'created_by', 'address', 'rtl_address')).data
    
    def get_review_no(self, instance):
        average_star, review_no = star_out_of_five(instance)
        return review_no
    
    def get_average_star(self, instance):
        average_star, review_no = star_out_of_five(instance)
        return average_star
    
    class Meta:
        model = Doctor
        fields = ('user', 'title', 'speciality_list', 'clinic_list', 'review_no', 'average_star')

class MedicalRecordFileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MedicalRecordFile
        exclude = ('medical_record',)

class RelativeSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    user = UserSerializer(fields=('id', 'full_name', 'rtl_full_name'), read_only=True)
    class Meta:
        model = Relative
        fields = '__all__'

class PatientSerializer(serializers.Serializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    user = UserSerializer(read_only=True, fields=('id', 'full_name', 'rtl_full_name', 'user_age', 'phone', 'gender', 'address', 'avatar'))
    blood_group = serializers.CharField(read_only=True)
    last_completed_appt = serializers.CharField(read_only=True)
    total_booked_appt = serializers.IntegerField(read_only=True)
    family_member_no = serializers.IntegerField(read_only=True)
    medical_record_no = serializers.IntegerField(read_only=True)
    share_record_to_all = serializers.BooleanField(default=True)


class DoctorUserSerializer(serializers.Serializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    user = UserSerializer(fields=('id', 'full_name', 'rtl_full_name'))
    class Meta:
        model = Doctor
        fields = ('user',)

class MedicalRecordTileSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    patient = serializers.SerializerMethodField(read_only=True)
    related_doctor = DoctorUserSerializer(fields=('user', ), read_only=True)
    record_file_no = serializers.SerializerMethodField(read_only=True)
    
    def get_record_file_no(self, instance):
        the_no = MedicalRecordFile.objects.filter(medical_record=instance).count() or 0
        return the_no
    
    def get_patient(self, instance):
        context = pick_patient(instance)
        return PatientRelativeSerializer(context, read_only=True, fields=('user',)).data
    
    class Meta:
        model = MedicalRecords
        fields = (
            'id', 'patient', 'related_doctor', 'record_file_no', 'title'
            )

def completed_appt_data(patient, doctor, is_patient=True):
    total_completed_appt_no = 0
    last_completed_appt = None
    the_filter = Q(status=Appointment.ApptStatus.COMPLETED)
    if is_patient:
        the_filter.add(Q(patient__user__id=patient.id, relative=None), Q.AND)
    else:
        the_filter.add(Q(relative__user__id=patient.id), Q.AND)
        
    appt_queryset = doctor.appointment_set.filter(the_filter).order_by('-appt_date')
    if appt_queryset.exists():
        last_completed_appt = appt_queryset.first().appt_date or None
        total_completed_appt_no = appt_queryset.count() or 0
    return last_completed_appt, total_completed_appt_no


def pick_patient(instance):
    is_patient = True
    try:
        if instance.relative is not None:
            is_patient = False
            patient = instance.relative
        else:
            patient = instance.patient
        the_result = completed_appt_data(patient.user, instance.related_doctor, is_patient)
        context = {
            'user': patient.user,
            'last_completed_appt': the_result[0],
            'total_booked_appt': the_result[1],
            'share_record_to_all': patient.share_record_to_all
        }
    except Exception as e:
        context = None
        print('inside the exception')
        print(e)
    return context


class PatientRelativeSerializer(serializers.Serializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    user = UserSerializer(read_only=True, fields=('id', 'full_name', 'rtl_full_name'))
    last_completed_appt = serializers.CharField(read_only=True)
    total_booked_appt = serializers.IntegerField(read_only=True)
    share_record_to_all = serializers.BooleanField(default=True)
    

class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    related_doctor = DoctorListTileSerializer(fields=('user', 'title', 'review_no', 'average_star', 'speciality_list'), read_only=True)
    files = MedicalRecordFileSerializer(many=True, read_only=True, source='medicalrecordfile_set')
    patient = serializers.SerializerMethodField(read_only=True)
    shared_with = serializers.SerializerMethodField(read_only=True)
    my_doctors = serializers.SerializerMethodField(read_only=True)
    
    def get_patient(self, instance):
        context = pick_patient(instance)
        return PatientRelativeSerializer(context, read_only=True).data
    
    def get_my_doctors(self, instance):
        response = []
        the_filter = Q(
            Q(Q(status=Appointment.ApptStatus.COMPLETED) 
            | Q(status=Appointment.ApptStatus.BOOKED))
            & ~Q(doctor__in=instance.shared_with.all())
            )
        try:
            id_list = instance.patient.appointment_set.filter(the_filter).values_list('doctor__user__id', flat=True).distinct()
            print('valuer of id_list')
            print(id_list)
            users = User.objects.filter(id__in=id_list)
            response = UserSerializer(users, many=True, fields=('id', 'full_name', 'rtl_full_name')).data
        except Exception as e:
            print('value fo e')
            print(e)
        return response
    
    def get_shared_with(self, instance):
        response = []
        if len(instance.shared_with.all()) > 0:
            id_list = instance.shared_with.all().values_list('user__id', flat=True)
            users = User.objects.filter(id__in=id_list)
            response = UserSerializer(users, many=True, fields=('id', 'full_name', 'rtl_full_name')).data
        return response
    
    class Meta:
        model = MedicalRecords
        fields = (
            'id', 'patient', 'related_doctor', 'shared_with', 'my_doctors', 'title',
            'general_access', 'updated_at', 'files'
            )

class SpecialityCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialityCategory
        fields = "__all__"


class CreateMedicalReocrdDataSerializer(serializers.Serializer):
    my_relatives = RelativeSerializer(read_only=True, many=True, fields=('user', 'share_record_to_all'))
    my_doctors = UserSerializer(read_only=True, many=True, fields=('id', 'full_name', 'rtl_full_name', 'avatar'))
    
        
class FindDoctorDataSerializer(serializers.Serializer):
    speciality_categories = SpecialityCategoryListSerializer(many=True)
    top_doctors = DoctorListTileSerializer(many=True)


class FeedbackDataSerializer(serializers.Serializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    feedback_no = serializers.IntegerField()
    average_star = serializers.DecimalField(max_digits=255, decimal_places=2)
    overall_experience = serializers.DecimalField(max_digits=255, decimal_places=2)
    doctor_checkup = serializers.DecimalField(max_digits=255, decimal_places=2)
    staff_behavior = serializers.DecimalField(max_digits=255, decimal_places=2)
    clinic_environment = serializers.DecimalField(max_digits=255, decimal_places=2)
    patient_no = serializers.IntegerField()
    completed_appt_no = serializers.IntegerField()
    experience_year = serializers.IntegerField()
    favorite_doctor_list = serializers.ListField(child=serializers.IntegerField())


class ApptListTileSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    doctor = DoctorListTileSerializer(read_only=True, fields=('user', 'title'))
    patient = RelativeSerializer(fields=('user',))
    relative = RelativeSerializer(fields=('user',))
    clinic = ClinicSerializer(fields=('id', 'address', 'district', 'city', 'clinic_name', 'rtl_clinic_name'))
    
    class Meta:
        model = Appointment
        fields = ('id', 'doctor', 'patient', 'relative', 'clinic', 'status',
                  'start_appt_time', 'end_appt_time', 'feedback_status', 'appt_date'
                  )
class ApptConditionTreatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApptConditionTreat
        fields = '__all__'

class ApptDetailSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    doctor = DoctorListTileSerializer(read_only=True, fields=('user', 'title'))
    patient = RelativeSerializer(fields=('user',))
    clinic = ClinicSerializer(fields=('id', 'address', 'district', 'city', 'clinic_name', 'rtl_clinic_name'))
    condition_treated = ApptConditionTreatSerializer(read_only=True, many=True)
    day_pattern = DaySchedulePatternSerializer(read_only=True, fields=('week_day', ))
    review = serializers.SerializerMethodField(read_only=True)
    feedback = serializers.SerializerMethodField(read_only=True)
    is_feedback_given = serializers.SerializerMethodField(read_only=True)
    
    def get_is_feedback_given(self, instance):
        is_given = False
        try:
            if instance.feedback:
                print('value fo instance.feedback ===--00----')
                print(instance.feedback.comment)
                print(instance.feedback.overall_experience)
                is_given = True
        except Exception as e:
            print('value fo erorororr')
            print(e)
        return is_given
    
    def get_review(self, instance):
        comment = None
        try:
            if instance.feedback:
                if instance.feedback.comment is not None and instance.feedback.comment != '' and instance.status == Appointment.ApptStatus.COMPLETED:
                    comment = instance.feedback.comment
        except Exception as e:
            print('value fo ---00000')
            print(e)
        return comment
    
    def get_feedback(self, instance):
        feedback = 3.5
        try:
            if instance.feedback:
                if instance.feedback.score_count is not None and instance.status == Appointment.ApptStatus.COMPLETED:
                    feedback = instance.feedback.score_count
        except Exception as e:
            pass
        return feedback
    
    class Meta:
        model = Appointment
        fields = ('id', 'doctor', 'patient', 'condition_treated', 'clinic', 'status', 'day_pattern', 'is_feedback_given',
                  'start_appt_time', 'end_appt_time', 'feedback_status', 'appt_date', 'remark', 'feedback', 'review'
                  )


class DoctorApptListSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer(fields=('id',), read_only=True)
    day_pattern = DaySchedulePatternSerializer(read_only=True, fields=('id', 'week_day', 'active'))
    class Meta:
        model = Appointment
        exclude = ('doctor', 'feedback_status', 'active', 'booked_at', 'condition_treated', 'patient', 'relative', 'status', 'remark')


class PatientProfileSettingSerializer(serializers.ModelSerializer):
    user = UserSerializer(fields = ('id', 'full_name', 'rtl_full_name', 'date_of_birth', 'avatar', 'gender'), read_only=True)
    selected_city = serializers.SerializerMethodField(read_only=True)
    selected_district = serializers.SerializerMethodField(read_only=True)
    blood_group = serializers.SerializerMethodField(read_only=True)
    district_list = serializers.SerializerMethodField(read_only=True)
    
    def get_selected_city(self, patient_instance):
        
        try:
            address = patient_instance.user.address
            the_city = address.city.name
        except:
            the_city = ''
        return the_city
    
    def get_selected_district(self, patient_instance):
        
        try:
            address = patient_instance.user.address
            the_district = address.district.name
        except:
            the_district = ''
        return the_district
    
    def get_blood_group(self, patient_instance):
        the_blood = ''
        try:
            the_blood = str(patient_instance.blood_group) 
        except:
            pass
        return the_blood
    
    def get_district_list(self, patient_instance):
        try:
            city_id = patient_instance.user.address.city.id
            raw_list = District.objects.filter(city__id=city_id) 
            the_list = DistrictSerializer(raw_list, many=True, fields=('id', 'name', 'rtl_name', 'city')).data
        except:
            the_list = []
        return the_list
    
    class Meta:
        model = Patient
        fields = '__all__'
        # exclude = ('share_record_to_all',)



# Ali part start 
# class UserSerializer(WritableNestedModelSerializer):
#     def __init__(self, *args, **kwargs):
#         dynamic_fields(self, args, kwargs)
#         super(self.__class__, self).__init__(*args, **kwargs)
#     address = AddressSerializer()

#     class Meta:

#         model = User

#         fields = "id", "full_name", "rtl_full_name", "gender", "phone", "email", "date_of_birth", "avatar", "address"

#         extra_kwargs = {
#             "phone": {"validators": [user_valid.phone_number]},
#             "email": {"validators": [user_valid.email]},
#         }

#         read_only_fields = ("id", "phone")




