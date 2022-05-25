# verify and signup user by the followign methods
# 1 - patient should be verify by social media (facebook and google) and phone number
# 2 - doctor should be verify by all methods e.g. social media, phone and email
# 3 - blogger, health ministry, admin are registered and verify manually

from django import forms
import django
from django.contrib.auth import get_user_model, authenticate, login
from django.core.exceptions import ValidationError

# from django.http import request
# from django.shortcuts import redirect
# from django.urls import reverse_lazy
from django.utils.functional import empty
from django.utils.translation import gettext as _

# from django.contrib import messages

from user.models import Doctor, Patient

User = get_user_model()


class LoginForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    phone = forms.CharField(
        label="Phone",
        widget=forms.TextInput(
            attrs={
                "name": "phone",
                "type": "text",
                "class": "form-control floating",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "name": "password",
                "type": "password",
                "class": "form-control floating",
            }
        )
    )

    def clean(self):
        request = self.request
        data = self.cleaned_data
        phone = data.get("phone")
        password = data.get("password")
        print('value fo password')
        print(password)
        if phone is empty:
            raise forms.ValidationError("Username field is empty")
        if not phone.isdigit():
            raise forms.ValidationError("Username field should only be numbers")
        if password is empty:
            raise forms.ValidationError("Password field is empty")
        qs = User.objects.filter(phone=phone)
        if not qs.exists():
            raise forms.ValidationError("Invalid credential")
        if qs.exists():
            activated_user = qs.filter(active=True)
            if activated_user.exists():
                user = authenticate(request, username=phone, password=password)
                if user is None:
                    raise forms.ValidationError("Invalid credential")
                if user.suspend:
                    raise forms.ValidationError(
                        "You Account has been suspend, please contact DOCTOR PLUS for more information"
                    )
                login(request, user)
                self.user = user
        return data


# class PatientRegisterForm(forms.ModelForm):
#     phone = forms.CharField(label='Phone', widget=forms.TextInput(attrs={
#         # "placeholder": _("Username"),
#         "name": "phone",
#         "type": "text",
#         "class": "form-control floating",

#     }))

#     full_name = forms.CharField(label='Name', widget=forms.TextInput(attrs={
#         # "placeholder": _("Username"),
#         "name": "full_name",
#         "type": "text",
#         "class": "form-control floating",

#     }))

#     password = forms.CharField(widget=forms.PasswordInput(attrs={
#         # "placeholder": _("Password"),
#         "name": "password",
#         "type": "password",
#         "class": "form-control floating",
#     }))

#     repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={
#         # "placeholder": _("Password"),
#         "name": "repeat_password",
#         "type": "password",
#         "class": "form-control floating",
#     }))


#     class Meta:
#         model = User
#         fields = ('phone', 'full_name',)

#     def clean(self):
#         print('inside the clean of form')
#         data = self.cleaned_data
#         print(data)
#         phone = data.get("phone")
#         name = data.get("full_name")
#         password = data.get('password')
#         repeat_password = data.get('repeat_password')
#         district = data.get('district')
#         city = data.get('city')
#         print('value of new entries')
#         print(district)
#         print(city)
#         if name is empty:
#             raise forms.ValidationError('Name field is empty')
#         if name.isdigit():
#             raise forms.ValidationError('Name field cannot be only numbers')
#         if phone is empty:
#             raise forms.ValidationError('Phone number field is empty')
#         if not phone.isdigit():
#             raise forms.ValidationError('Phone number field should only be numbers')
#         if password is empty:
#             raise forms.ValidationError('Password field is empty')
#         if repeat_password is empty:
#             raise forms.ValidationError('Password field is empty')
#         if password and repeat_password and password != repeat_password:
#             raise ValidationError("Password don't match")
#         user = User.objects.filter(phone=phone, active=True)
#         if user.exists():
#             raise ValidationError('A user is already registered to this number')
#         return data

#     def save(self, commit=True):
#         # form_valid() method gets executed before this method and it has user.is_authenticated as well
#         # and clean gets executed before form_valid()
#         user = super(PatientRegisterForm, self).save(commit=False)
#         print('inside of save')
#         # print(user)
#         user.set_password(self.cleaned_data["password"])
#         user.active = False
#         if commit:
#             patient_user = user.save()
#             patient = Patient.objects.create(user=patient_user)
#             print(patient)
#         return user


# class DoctorRegisterForm(forms.Form):
#     phone = forms.CharField(label='Phone', widget=forms.TextInput(attrs={
#         "name": "phone",
#         "type": "text",
#         "class": "form-control floating",

#     }))

#     full_name = forms.CharField(label='Name', widget=forms.TextInput(attrs={
#         "name": "full_name",
#         "type": "text",
#         "class": "form-control floating",

#     }))

#     email = forms.CharField(label='Email', widget=forms.TextInput(attrs={
#         "name": "email",
#         "type": "text",
#         "class": "form-control floating",

#     }))

#     password = forms.CharField(widget=forms.PasswordInput(attrs={
#         "name": "password",
#         "type": "password",
#         "class": "form-control floating",
#     }))

#     repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={
#         "name": "repeat_password",
#         "type": "password",
#         "class": "form-control floating",
#     }))

#     # class Meta:
#     #     model = User
#     #     fields = ('phone', 'full_name', 'email',)

#     def __init__(self, request, *args, **kwargs):
#         self.request = request
#         super(DoctorRegisterForm, self).__init__(*args, **kwargs)

#     def clean(self):
#         print('inside the clean of form')
#         data = self.cleaned_data
#         print(data)
#         phone = data.get("phone")
#         name = data.get("full_name")
#         email = data.get("email")
#         password = data.get('password')
#         repeat_password = data.get('repeat_password')
#         if name is empty:
#             raise forms.ValidationError('Name field is empty')
#         if name.isdigit():
#             raise forms.ValidationError('Name field cannot be only numbers')
#         if email is empty:
#             raise forms.ValidationError('Email field is empty')
#         if email.isdigit():
#             raise forms.ValidationError('Invalid email format')
#         if phone is empty:
#             raise forms.ValidationError('Phone number field is empty')
#         if not phone.isdigit():
#             raise forms.ValidationError('Phone number field should only be numbers')
#         if password is empty:
#             raise forms.ValidationError('Password field is empty')
#         if repeat_password is empty:
#             raise forms.ValidationError('Password field is empty')
#         if password and repeat_password and password != repeat_password:
#             raise ValidationError("Password don't match")
#         user = User.objects.filter(phone=phone, active=True)
#         if user.exists():
#             raise ValidationError('A user is already registered to this number')
#         return data

# def save(self, commit=True):
#     user = super(DoctorRegisterForm, self).save(commit=False)
#     print('inside of save')
#     user.set_password(self.cleaned_data["password"])
#     user.active = False
#     if commit:
#         user.save()
#         doctor = Doctor.objects.create(user=user)
#         print(doctor)
#     return user


class AdoptSocialUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "full_name", "phone"
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            # "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            # "gender": forms.Select(attrs={"class": "form-control"}),
            # "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
