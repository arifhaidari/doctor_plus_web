from django.dispatch import receiver
from DoctorPlus.utils import star_out_of_five, calculate_patient_appt
import appointment
from appointment.models import Appointment, Feedback
import itertools
from django.db.models import Q, F, fields
from notification.models import Notification
from rest_api.doctor_api.serializers import CitySerializer, DistrictSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSlidingSerializer
from rest_framework import permissions
from user.models import Patient, RelativeRelation, BloodGroup, Doctor, Service, Speciality, DoctorTitle, User as UserModel
from blog.models import Post, PostImages, PostCategory
from home.models import City, District
from django.db.models import Sum
from django.contrib.auth import get_user_model
User = get_user_model()

class PatientTokenObtainSerializer(TokenObtainPairSerializer):
         # this custom login is only for doctor .... for patient create another one 
    # if a patient user try to login in doctor app it should shows that it is you are not doctor
    def validate(self, attrs):
        print('value fo validate')
        data = super().validate(attrs)
        token = self.get_token(self.user)
        # for pair TokenObtainPairSerializer
        data['is_patient'] = False
        if is_patient(self.user.user_type):
            print('it is a patient')
            data['refresh'] = str(token)
            data['access'] = str(token.access_token)
            patient_data = patient_brief_data(self.user, data)
            data['is_patient'] = True
        return patient_data if data['is_patient'] else data


def patient_brief_data(user, data):
    the_filter = Q(patient=user.patient, status=Appointment.ApptStatus.COMPLETED)
    patient_completed_appt_no = Appointment.objects.filter(relative=None).filter(the_filter).count() or 0
    relative_completed_appt_no = Appointment.objects.filter(~Q(relative=None)).filter(the_filter).count() or 0
    try:
        the_avatar = user.avatar.url
    except:
        the_avatar = None
    
    try:
        city = user.address.city.name
        district = user.address.district.name
    except:
        city = None
        district = None
    data['id'] = user.id
    data['full_name'] = user.full_name
    data['is_active'] = user.active
    data['rtl_full_name'] = user.rtl_full_name
    data['share_record_to_all'] = user.patient.share_record_to_all
    data['phone'] = user.phone
    data['gender'] = user.gender
    data['avatar'] = the_avatar
    data['city'] = city
    data['district'] = district
    data['patient_completed_appt_no'] = patient_completed_appt_no
    data['relative_completed_appt_no'] = relative_completed_appt_no
    # cities = City.objects.all()
    # data['cities'] = CitySerializer(cities, many=True).data
    # districts = District.objects.all()
    # data['districts'] = DistrictSerializer(districts, many=True).data
    return data

class PatientBasicInfoSerializer(serializers.ModelSerializer):
    patient_completed_appt_no = serializers.IntegerField(read_only=True)
    relative_completed_appt_no = serializers.IntegerField(read_only=True)
    cities = serializers.SerializerMethodField(read_only=True)
    # districts = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'full_name', 'rtl_full_name', 'avatar', 'phone', 'gender', 'patient_completed_appt_no', 'relative_completed_appt_no', 'cities')


is_patient = lambda user_type: UserModel.Types.Patient == user_type

class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    # this custom login is only for doctor .... for patient create another one 
    # if a patient user try to login in doctor app it should shows that it is you are not doctor
    def validate(self, attrs):
        print('value fo validate')
        data = super().validate(attrs)
        token = self.get_token(self.user)
        data['is_doctor'] = False
        if not is_patient(self.user.user_type):
            print('it is not a patient')
            data['refresh'] = str(token)
            data['access'] = str(token.access_token)
            user_dash_data = user_dashboard_brief(self.user, data)
            data['is_doctor'] = True
        
        return user_dash_data if data['is_doctor'] else data

def user_dashboard_brief(user, data):
    average_star, feedback_no = star_out_of_five(user.doctor)
    # patients = [x.get("m_patient") for x in my_patient_raw if x.get("m_relative") is None]
    # relatives = [x.get("m_relative") for x in my_patient_raw if x.get("m_relative") is not None]
    # my_patients = list(itertools.chain(patients, relatives))
    # pateint_relative_list = User.objects.filter(id__in=my_patients)
    is_unseen_note = False
    notification_queryset = Notification.objects.filter(receiver=user, seen=False)
    if notification_queryset.exists():
        is_unseen_note = True
    booked_appt_no, patient_no = calculate_patient_appt(user.doctor, operation='doctor')
    print('value of is_unseen_note')
    print(is_unseen_note)
    # print(booked_appt_no)
    try:
        the_avatar = user.avatar.url
    except:
        the_avatar = None

    data['id'] = user.id
    data['full_name'] = user.full_name
    data['rtl_full_name'] = user.full_name
    data['is_active'] = user.active
    data['is_unseen_note'] = is_unseen_note
    data['is_profile_completed'] = user.doctor.professional_status
    data['is_profile_on_progress'] = user.doctor.is_profile_on_progress
    data['phone'] = user.phone
    data['avatar'] = the_avatar
    data['title'] = user.doctor.title.title
    data['farsi_title'] = user.doctor.title.farsi_title
    data['pashto_title'] = user.doctor.title.pashto_title
    data['average_star'] = average_star or 1.0
    data['patient_no'] = patient_no or 0
    data['booked_appt_no'] = booked_appt_no or 0
    data['feedback_no'] = feedback_no or 0
    return data

class UserBasicInfoSerializer(serializers.ModelSerializer):
    title_name = serializers.CharField(read_only=True)
    farsi_title = serializers.CharField(read_only=True)
    pashto_title = serializers.CharField(read_only=True)
    patient_no = serializers.IntegerField(read_only=True)
    booked_appt_no = serializers.IntegerField(read_only=True)
    feedback_no = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'full_name', 'rtl_full_name', 'avatar', 'title_name', 'farsi_title', 'pashto_title', 'patient_no', 'booked_appt_no', 'feedback_no')


    

# create patient and doctor 
class CreateDoctorPatientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    blood_group = serializers.CharField(write_only=True)
    title = serializers.CharField(write_only=True)
    user_type = serializers.CharField(write_only=True, default='Patient')
    
    class Meta:
        model = User
        fields = ("id", "phone", "full_name", "rtl_full_name", "blood_group", "gender", "user_type", "title", "blood_group", "password", "confirm_password")
    
    def validate_phone(self, value):
        print('value of validate phone ')
        print(len(value));
        if len(value) != 10:
            raise serializers.ValidationError('Phone should be 10 digits')
        is_user = User.objects.filter(phone=value)
        print('value fo is_user')
        print(is_user.exists())
        if is_user.exists():
            raise serializers.ValidationError('Yo the phone is already exist')
        return value
    
    def validate(self, data):
        pw = data.get("password")
        pw2 = data.get("confirm_password")
        
        if len(data["password"]) < 6 or len(data['password']) > 20:
            raise serializers.ValidationError("Password is too short. it should be 6 chars at least.")
        if pw != pw2:
            raise serializers.ValidationError("Passwords must match")
        print('value of there is no error neither')
        return data

    def create(self, data):
        print('value of data')
        print(data)
        # if 2 == 2:
        #     raise serializers.ValidationError('things goes perfect')
        try:
            user = User.objects.create_user(
                phone=data["phone"],
                full_name = data['full_name'],
                gender = data['gender'],
                user_type = data['user_type'],
                password=data["password"],
                )
            print('value fo user type')
            print(data['user_type'])
            if data['user_type'] == User.Types.Doctor:
                title = DoctorTitle.objects.get(title=data['title'])
                Doctor.objects.create(user=user, title=title)
            else:
                blood_name = data['blood_group']
                the_blood = BloodGroup.objects.get(name=blood_name)
                Patient.objects.create(user=user, blood_group=the_blood)
        except Exception as e:
            print('value of e in erorrorororor')
            print(e)
            user = None
        return user

    
