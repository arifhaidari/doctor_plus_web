# Social imports
from ast import operator
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from DoctorPlus.mixins import request_data_validator

from .permissins import *
from datetime import date, datetime, timedelta

# drf imports
from rest_framework import mixins, generics
from user.models import OTPVerification

from . import serializers as ser
from django.contrib.auth import get_user_model

User = get_user_model()


""" Authentication APIs """


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


# Doctor basic info
class BasicInfo(generics.ListAPIView):
    serializer_class = ser.UserBasicInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    # lookup_field = 'pk'
    
    def get(self, request, *args, **kwargs):
        basic_info = ser.user_dashboard_brief(self.request.user, {})
        return Response(basic_info)


# Doctor basic info
class PatientBasicInfo(generics.ListAPIView):
    serializer_class = ser.PatientBasicInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    # lookup_field = 'pk'
    
    def get(self, request, *args, **kwargs):
        # delete previous appt here
        basic_info = ser.patient_brief_data(self.request.user, {})
        # delete the previous booked and pending appts
        return Response(basic_info)

# Login Doctor
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = ser.CustomTokenObtainSerializer

# Login Patient
class PatientTokenObtainPairView(TokenObtainPairView):
    serializer_class = ser.PatientTokenObtainSerializer


# Registration Patient
class RegisterDoctorPatient(generics.CreateAPIView):
    serializer_class         = ser.CreateDoctorPatientSerializer
    permission_classes       = [AnonPermissionOnly]

# Registration Doctor
# class RegisterUser(generics.CreateAPIView):
#     serializer_class         = ser.CreateUserSerializer
#     permission_classes       = [AnonPermissionOnly]


class OTPVerificationView(APIView):
    permission_classes = [AnonPermissionOnly]
    
    def post(self, request, *args, **kwargs):
        phone_otp = request.data.get('phone_otp', None)
        the_round = request.data.get('the_round', None)
        operation = request.data.get('operation', None)
        # operation = verify, forget_password
        now_date_time = datetime.now()
        # two_days_ago = now_date_time - timedelta(days=2)
        # OTPVerification.objects.filter(timestamp=two_days_ago).delete()
        message = 'success'
        print('value of phone_otp, the_round, operation')
        print(phone_otp, the_round, operation)
        try:
            if request_data_validator([phone_otp, the_round, operation]):
                if the_round == 'create_round':
                    # create the otp here and save it otpverification model
                    is_user = User.objects.filter(phone=phone_otp)
                    if is_user.exists():
                        is_phone = OTPVerification.objects.filter(phone=phone_otp)
                        if is_phone.exists():
                            is_phone.delete()
                        OTPVerification.objects.create(
                            phone = phone_otp,
                        )
                    else:
                        message = 'no_account'
                else:
                    # recieve_round
                    is_otp = OTPVerification.objects.filter(six_digit=phone_otp)
                    if is_otp.exists():
                        the_otp = is_otp.first()
                        time_difference = now_date_time - datetime.strptime(str(the_otp.timestamp).split('.')[0], '%Y-%m-%d %H:%M:%S')
                        time_diff_in_hour = (time_difference.total_seconds()/60)/60
                        if time_diff_in_hour > 10:
                            message = 'expired'
                        else:
                            print('activate user')
                            if operation == 'verify':
                                print('value of phone=the_otp.phone')
                                print(the_otp.phone)
                                the_user = User.objects.get(phone=the_otp.phone)
                                the_user.active = True
                                the_user.save()
                                print('value of the_user.save()')
                    else:
                        message = 'not_exist'
            else:
                message = 'field_error'
        except Exception as e:
            print('value of e')
            print(e)
            message = 'fail'
        return Response({'message': message})