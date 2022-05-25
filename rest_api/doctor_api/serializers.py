from django.db.models import fields
from django.db.models.fields import files
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from django.db.models import Q

from drf_writable_nested.serializers import WritableNestedModelSerializer
from doctor.models import EducationDegree, DegreeType
import rest_api

from user import validators as user_valid
from appointment.models import (
    Appointment,
    ApptConditionTreat,
    Feedback,
    FeedbackReplies,
    DaySchedulePattern,
    WeekDays,
    DeactivatedApptSlot,
)
# from rest_api.patient_api import serializers as patient_serializer
from user.models import (Patient, User, Relative, Doctor, 
                         Service, Condition, Speciality, DoctorTitle, FreeServiceSchedule
                         )

from doctor.models import Clinic, Education, Award, Experience, EducationDegree
from home.models import Address, City, District
from medicalrecord.models import MedicalRecordFile, MedicalRecords
from notification.models import Notification
# from notification import review_notifications


def dynamic_fields(self, args, kwargs):
    fields = kwargs.pop("fields", None)
    exclude = kwargs.pop("exclude", None)
    super(self.__class__, self).__init__(*args, **kwargs)
    # setting fields dynamically
    fields and [self.fields.pop(field_name) for field_name in set(self.fields) - set(fields)]
    exclude and [self.fields.pop(field_name) for field_name in set(self.fields) if field_name in set(exclude)]
    # if fields is not None:
    #     allowed = set(fields)
    #     existing = set(self.fields)
    #     # [self.fields.pop(field_name) for field_name in existing - allowed]
    #     for field_name in existing - allowed:
    #         self.fields.pop(field_name)
    # if exclude is not None:
    #     exclude_fields = set(exclude)
    #     existing = set(self.fields)
    #     for field_name in existing:
    #         if field_name in exclude_fields:
    #             self.fields.pop(field_name)


# Eblis Edition
# ============== # =====================
class ClinicScheduleBriefSerializer(serializers.ModelSerializer): 
    time_slot_duration = serializers.CharField(read_only=True)
    start_day_time = serializers.CharField(read_only=True)
    end_day_time = serializers.CharField(read_only=True)
    total_booked_appt_no = serializers.CharField(read_only=True)
    class Meta:
        model = Clinic
        fields = ('id', 'clinic_name', 'rtl_clinic_name', 'time_slot_duration', 'start_day_time', 'end_day_time', 'total_booked_appt_no')


class BookedApptListSerializer(serializers.ModelSerializer):
    appt_id = serializers.IntegerField(read_only=True)
    patient_id = serializers.IntegerField(read_only=True)
    clinic_id = serializers.IntegerField(read_only=True)
    patient_name = serializers.CharField(read_only=True)
    rtl_patient_name = serializers.CharField(read_only=True)
    patient_phone = serializers.CharField(read_only=True)
    patient_age = serializers.CharField(read_only=True)
    avatar = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)
    clinic_name = serializers.CharField(read_only=True)
    rtl_clinic_name = serializers.CharField(read_only=True)
    city = serializers.CharField(read_only=True)
    district = serializers.CharField(read_only=True)
    rtl_city = serializers.CharField(read_only=True)
    rtl_district = serializers.CharField(read_only=True)
    week_day = serializers.CharField(read_only=True)
    rtl_week_day = serializers.CharField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ('appt_id', 'patient_id', 'clinic_id', 'patient_name', 'rtl_patient_name', 'patient_phone', 'patient_age', 'avatar', 'gender', 'clinic_name', 'rtl_clinic_name', 
                  'week_day', 'rtl_week_day', 'start_appt_time', 'end_appt_time', 'appt_date', 'booked_at', 'city', 'rtl_city', 'district', 'rtl_district'
                  )


class CitySerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)

    class Meta:
        model = City
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    city = CitySerializer(read_only=True, exclude=('id',))
    class Meta:
        model = District
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    city = CitySerializer(read_only=True, exclude=('id',))
    district = DistrictSerializer(read_only=True, exclude=('id','city'))
    
    class Meta:
        model = Address
        fields = '__all__'
    
class UserSerializer(WritableNestedModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)

    address = AddressSerializer(read_only=True, exclude=("user", "id", "latitude", "longtitude"))
    # we set many equal to false while it is not iterable

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "rtl_full_name",
            "gender",
            "phone",
            "user_age",
            "date_of_birth",
            "avatar",
            "active",
            "address",
        )
        read_only_fields = "id", "phone"
        # extra_kwargs = {
        #     "phone": {"validators": [user_valid.phone_number]},
        #     "email": {"validators": [user_valid.email]},
        # }
class ClinicSerializer(WritableNestedModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    city = CitySerializer(read_only=True, exclude=("id",))
    district = DistrictSerializer(read_only=True, exclude=('id', 'city'))

    class Meta:
        model = Clinic
        # fields = "__all__"
        exclude = ("doctor",)
        read_only_fields = "id", "created_by", "active"

    # def create(self, validated_data):
    #     update_data = {
    #         "active": False,
    #         "created_by": self.context["request"].user.doctor,
    #     }
    #     validated_data.update(update_data)
    #     print("validated_data ", validated_data)
    #     return super(self.__class__, self).create(validated_data)
class WeekDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekDays
        # fields = "__all__"
        exclude=('id',)


class DaySchedulePatternSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    # clinic = ClinicSerializer(read_only=True, fields=("id", "clinic_name", "rtl_clinic_name"))
    week_day = WeekDaysSerializer(read_only=True)
    class Meta:
        model = DaySchedulePattern
        exclude = ("doctor", "clinic")

class ClinicApptSerializer(serializers.ModelSerializer):
    # clinic = ClinicSerializer(fields=("id", "clinic_name", "rtl_clinic_name"))
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    day_pattern = DaySchedulePatternSerializer(exclude=('time_slot_duration', 'start_day_time', 'end_day_time', 'id'))
    class Meta:
        model = Appointment
        fields = (
            "id",
            "start_appt_time",
            "end_appt_time",
            "status",
            "active",
            "appt_date",
            # "clinic",
            "day_pattern",
        )
        read_only_fields = ('id', )

class PatientBookedApptSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            "id",
            "start_appt_time",
            "end_appt_time",
            "status",
            "active",
            "appt_date",
        )
        read_only_fields = ('id', )

class MyPatientListSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    user = UserSerializer(read_only=True, exclude=('active',))
    total_booked_appt = serializers.SerializerMethodField('total_booked_appt_func', read_only=True)
    last_completed_appt = serializers.SerializerMethodField('last_completed_appt_func', read_only=True)
    blood_group = serializers.SerializerMethodField('blood_group_fun', read_only=True)
    
    def total_booked_appt_func(self, patient):
        doctor = self.context['request'].user.doctor
        appt_count = total_booked_appt(doctor, patient)
        return appt_count
    
    def last_completed_appt_func(self, patient):
        doctor = self.context['request'].user.doctor
        patient_object = Patient.objects.filter(user__id=patient.user.id)
        last_completed_appt = ''
        if patient_object.exists():
            last_completed_appt_queryset = doctor.appointment_set.filter(
                patient=patient, status=Appointment.ApptStatus.COMPLETED
                )
            if last_completed_appt_queryset.exists():
                last_completed_appt = last_completed_appt_queryset.order_by('-appt_date').first().appt_date
        else:
            last_completed_appt_queryset = doctor.appointment_set.filter(
                relative=patient, status=Appointment.ApptStatus.COMPLETED
                )
            if last_completed_appt_queryset.exists():
                last_completed_appt = last_completed_appt_queryset.order_by('-appt_date').first().appt_date
        
        return last_completed_appt
    
    def blood_group_fun(self, instance):
        if instance.blood_group:
            return instance.blood_group.name
        return None
    
    class Meta:
        model = Patient
        fields = ('blood_group', 'user', 'total_booked_appt', 'last_completed_appt')

class MedicalRecordFileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MedicalRecordFile
        # fields = '__all__'
        exclude = "id", "medical_record"

class MedicalRecordsSerializer(serializers.ModelSerializer):
    file = MedicalRecordFileSerializer(many=True, source='medicalrecordfile_set')
    class Meta:
        model = MedicalRecords
        fields = "title", "file",
        # read_only_fields = ("patient",)

    # def to_representation(self, instance):
    #     data = super(self.__class__, self).to_representation(instance)
    #     data["patient"] = f"{instance.patient.patient} | {instance.patient.relative}"
    #     return data



def total_booked_appt(doctor, patient):
    appt_count = 0
    appt_object = doctor.appointment_set.filter(status=Appointment.ApptStatus.COMPLETED)
    relative_filter = appt_object.filter(relative__user__id=patient.user.id)
    if relative_filter is not None and len(relative_filter) != 0:
        appt_count = relative_filter.count()
    else:
        appt_count = appt_object.filter(patient__user__id=patient.user.id, relative=None).count() or 0
    return appt_count

class DegreeTypeSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    class Meta:
        model = DegreeType
        fields = '__all__'
        read_only_fields = ("id",)

class EducationDegreeSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    degree_type = DegreeTypeSerializer(read_only=True, exclude=('farsi_name', 'pashto_name'))
    class Meta:
        model = EducationDegree
        # exclude = ("degree_type",)
        fields = '__all__'
        read_only_fields = ("id",)

class EducationSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    degree = EducationDegreeSerializer(read_only=True, )
    class Meta:
        model = Education
        exclude = ("doctor",)
        read_only_fields = ("id",)

    # def create(self, validated_data):
    #     validated_data.update({"doctor": self.context["request"].user.doctor})
    #     return super().create(validated_data)


class AwardSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    class Meta:
        model = Award
        exclude = ("doctor",)
        read_only_fields = ("id",)

    # def create(self, validated_data):
    #     validated_data.update({"doctor": self.context["request"].user.doctor})
    #     return super().create(validated_data)


class ExperienceSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    class Meta:
        model = Experience
        exclude = ("doctor",)
        read_only_fields = ("id",)

    # def create(self, validated_data):
    #     validated_data.update({"doctor": self.context["request"].user.doctor})
    #     return super().create(validated_data)

class DoctorTitleSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    class Meta:
        model = DoctorTitle
        exclude = ("id",)
        read_only_fields = ("id",)

class CitySerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    class Meta:
        model = City
        fields = '__all__'
        read_only_fields = ("id",)

class DistrictSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    city = CitySerializer(read_only=True, exclude=('name', 'rtl_name'))
    class Meta:
        model = District
        fields = '__all__'
        read_only_fields = ("id",)

class SpecialitySerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    class Meta:
        model = Speciality
        # fields = "__all__"
        exclude = ("speciality_category", )


class ServiceSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    speciality = SpecialitySerializer(exclude=('name', 'farsi_name', 'pashto_name'))
    class Meta:
        model = Service
        fields = "__all__"


class ConditionSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    speciality = SpecialitySerializer(exclude=('name', 'farsi_name', 'pashto_name'))
    class Meta:
        model = Condition
        fields = "__all__"

class FreeServiceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeServiceSchedule
        exclude = ('doctor', 'updated_at')
        read_only_fields = ('id',)


class DoctorBasicInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, fields=('full_name', 'rtl_full_name', 'date_of_birth', 'gender', 'avatar'))
    free_service_schedule = FreeServiceScheduleSerializer(source="freeserviceschedule", read_only=True)
    title = DoctorTitleSerializer(read_only=True)
    
    class Meta:
        model = Doctor
        fields = ('user', 'doc_license_no', 'fee', 'title', 'is_free_service', 'free_service_schedule')


class ViewDoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, exclude=('active',))
    title = DoctorTitleSerializer(read_only=True)
    speciality_list = SpecialitySerializer(source="speciality", many=True, read_only=True, exclude=('speciality_category',))
    service_list = ServiceSerializer(source="service", many=True, read_only=True)
    condition_list = ConditionSerializer(source="condition", many=True, read_only=True)
    free_service_schedule = FreeServiceScheduleSerializer(source="freeserviceschedule", read_only=True)
    clinic_list = ClinicSerializer(
        many=True, read_only=True, source="clinic_set", 
        exclude=("created_at", "doctor", "latitude", "longtitude", "active")
        )
    education_list = EducationSerializer(read_only=True, many=True, source='education_set')
    experience_list = ExperienceSerializer(read_only=True, many=True, source='experience_set')
    award_list = AwardSerializer(read_only=True, many=True, source='award_set')

    class Meta:
        model = Doctor
        fields = (
            'user', 'title', 'doc_license_no', 'fee', 'is_free_service', 'bio', 'farsi_bio', 
            'pashto_bio', 'professional_status', 'speciality_list', 'service_list',
            'condition_list', 'free_service_schedule', 'clinic_list', 'education_list', 'experience_list', 'award_list'
            )


class CareServicesSerializer(serializers.Serializer):
    speciality_list = SpecialitySerializer(many=True)
    condition_list = ConditionSerializer(many=True)
    service_list = ServiceSerializer(many=True)
    selected_speciality_list = SpecialitySerializer(many=True)
    selected_condition_list = ConditionSerializer(many=True)
    selected_service_list = ServiceSerializer(many=True)


class CityDistrictListSerializer(serializers.Serializer):
    city_list = CitySerializer(many=True)
    district_list = DistrictSerializer(many=True)



class BioSerializer(serializers.Serializer):
    english_bio = serializers.CharField()
    faris_bio = serializers.CharField()
    pashto_bio = serializers.CharField()
    
    
class FeedbackRepliesSerializer(serializers.ModelSerializer):
    author = UserSerializer(fields=("full_name", "rtl_full_name", "avatar"), read_only=True)
    # feedback_id = serializers.IntegerField(write_only=True)
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackReplies
        fields = "id", "author", "is_me", "reply", "timestamp"
        read_only_fields = "id", "feedback", "author"

    def create(self, validated_data):
        print("validated_data  : ", validated_data)
        validated_data.update({"author": self.context["request"].user})
        instance = super().create(validated_data)
        # sending the new reply notification to patient
        # review_notifications.create_feedback_relay(instance.feedback.id, instance.reply)
        # review_relplied_by_doctor(appt_object, reply)
        return instance

    # def update(self, instance, validated_data):
    #     print('inside the update of serializer')
    #     print(validated_data)
    #     print(instance)
    #     print(self)
    #     if self.context["request"].user == instance.author:
    #         return super(self.__class__, self).update(instance, validated_data)
    #     raise serializers.ValidationError(data="your are not the author to edit.")

    def get_is_me(self, instance):
        return instance.author == self.context["request"].user

class ApptSerializer(serializers.ModelSerializer):
    user_patient = serializers.SerializerMethodField("get_patient_func", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "user_patient",
        )
        # read_only_fields = "id"

    def get_patient_func(self, instance):
        patient_object = instance.patient
        return {
            'id': patient_object.user.id,
            'full_name': patient_object.user.full_name,
            'rtl_full_name': patient_object.user.rtl_full_name,
            'avatar': patient_object.user.avatar.url,
        }

class FeedbackSerializer(serializers.ModelSerializer):
    replies = FeedbackRepliesSerializer(many=True, read_only=True)
    appointment = ApptSerializer()

    class Meta:
        model = Feedback
        fields = (
            "id",
            "appointment",
            "comment",
            "timestamp",
            "score_count",
            "overall_experience",
            "doctor_checkup",
            "staff_behavior",
            "clinic_environment",
            "replies",
        )


class NotificationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="get_category_display")
    from rest_api.patient_api.serializers import ApptListTileSerializer
    appt = ApptListTileSerializer(fields=('id', 'doctor'))
    class Meta:
        model = Notification
        exclude = ("receiver",)

class ApptConditionTreatSerializer(serializers.ModelSerializer):
    __init__ = lambda self, *args, **kwargs: dynamic_fields(self, args, kwargs)
    
    class Meta:
        model = ApptConditionTreat
        fields = '__all__'
    

class ApptDetailSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer(read_only=True, fields=('clinic_name', 'rtl_clinic_name'))
    day_pattern = DaySchedulePatternSerializer(read_only=True, fields=('week_day',))
    condition_treated = ApptConditionTreatSerializer(read_only=True, exclude=('id',), many=True)
    review = serializers.SerializerMethodField(read_only=True)
    feedback = serializers.SerializerMethodField(read_only=True)
    
    def get_review(self, instance):
        comment = None
        try:
            if instance.feedback:
                if instance.feedback.comment is not None and instance.feedback.comment != '' and instance.status == Appointment.ApptStatus.COMPLETED:
                    comment = instance.feedback.comment
        except Exception as e:
            pass
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
        fields = ('clinic', 'review', 'feedback', 'start_appt_time', 'end_appt_time', 'appt_date', 'day_pattern', 'status', 'remark', 'condition_treated')


