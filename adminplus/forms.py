from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from user.models import Speciality, Condition, Service  # , SpecialityCategory
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory


class SpecialityForm(forms.ModelForm):
    class Meta:
        model = Speciality
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "farsi_name": forms.TextInput(attrs={"class": "form-control", "dir": "rtl"}),
            "pashto_name": forms.TextInput(attrs={"class": "form-control", "dir": "rtl"}),
            "speciality_category": forms.Select(attrs={"class": "form-control"}),
        }


condition_formset = inlineformset_factory(
    Speciality,
    Condition,
    fields="__all__",
    extra=3,
    widgets={
        "name": forms.TextInput(attrs={"class": "col-md-4"}),
        "farsi_name": forms.TextInput(attrs={"class": "col-md-4"}),
        "pashto_name": forms.TextInput(attrs={"class": "col-md-3"}),
    },
)

service_formset = inlineformset_factory(
    Speciality,
    Service,
    fields="__all__",
    extra=3,
    widgets={
        "name": forms.TextInput(attrs={"class": "col-md-4"}),
        "farsi_name": forms.TextInput(attrs={"class": "col-md-4"}),
        "pashto_name": forms.TextInput(attrs={"class": "col-md-3"}),
    },
)


class AdminEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("full_name", "rtl_full_name", "gender", "phone", "email", "date_of_birth", "avatar")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "rtl_full_name": forms.TextInput(attrs={"class": "form-control", "dir": "rtl"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields["old_password"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password1"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password2"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password2"].label = "Confirm Password"
