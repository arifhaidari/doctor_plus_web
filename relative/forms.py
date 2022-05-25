from django import forms
from django.contrib.auth.forms import UserCreationForm  # , UserChangeForm
from django.db.models import Q
from user.models import Relative, User, Doctor
from medicalrecord.models import MedicalRecords
from appointment.models import Appointment


# class AddUserForRelativeForm(UserCreationForm):
#     def __init__(self, *args, **kwargs):
#         super(AddUserForRelativeForm, self).__init__(*args, **kwargs)
#         self.initial["gender"] = "Male"
#         self.fields["password1"].required = False
#         self.fields["password2"].required = False
#         self.fields["password1"].widget.attrs["autocomplete"] = "off"
#         self.fields["password2"].widget.attrs["autocomplete"] = "off"

#     class Meta:
#         model = User
#         fields = ("full_name", "rtl_full_name", "gender", "date_of_birth", "phone", "email", "avatar")
#         labels = {
#             "full_name": "Full Name",
#             "rtl_full_name": "Name in Dari/Pashto",
#             "avatar": "Photo",
#         }
#         widgets = {
#             "full_name": forms.TextInput(attrs={"class": "form-control"}),
#             "rtl_full_name": forms.TextInput(attrs={"class": "form-control"}),
#             "gender": forms.Select(attrs={"class": "form-control"}),
#             "date_of_birth": forms.widgets.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "phone": forms.TextInput(attrs={"class": "form-control"}),
#             "avatar": forms.FileInput(attrs={"class": "form-control"}),
#         }

#     def clean_full_name(self):
#         name = self.cleaned_data.get("full_name")
#         if name and not any(str(x).isalpha() for x in name):
#             raise forms.ValidationError("Name should only contains letters.")
#         return name

#     def clean_phone(self):
#         phone = self.cleaned_data.get("phone")
#         if not any(str(x).isdigit() for x in phone):
#             raise forms.ValidationError("Phone Number should only contain numbers.")
#         return phone

#     def save(self, commit=True):
#         user = super(AddUserForRelativeForm, self).save(commit=False)
#         user.set_unusable_password()
#         if commit:
#             user.save()
#         return user


# class AddRelativeForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(AddRelativeForm, self).__init__(*args, **kwargs)
#         self.initial["relation"] = 3

#     class Meta:
#         model = Relative
#         fields = ("relation", "blood_group")
#         labels = {"relation": "RelativeRelation"}
#         widgets = {
#             "relation": forms.Select(attrs={"class": "form-control"}),
#             "blood_group": forms.Select(attrs={"class": "form-control"}),
#         }


