from django import forms
from appointment.models import Feedback, FeedbackReplies
from medicalrecord.models import MedicalRecords
from user.models import Doctor, User
from appointment.models import Appointment
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm


class CreateFeedBackRepliesForm(forms.ModelForm):
    class Meta:
        model = FeedbackReplies
        fields = ("feedback", "author", "reply")


class CreateFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("appointment", "comment", "overall_experience", "doctor_checkup", "staff_behavior", "clinic_environment")
        widgets = {
            "appointment": forms.HiddenInput(),
            "comment": forms.Textarea(attrs={"rows": "1", "class": "form-control d-block "}),
            "overall_experience": forms.Select(attrs={"class": "form-control"}),
            "doctor_checkup": forms.Select(attrs={"class": "form-control"}),
            "staff_behavior": forms.Select(attrs={"class": "form-control"}),
            "clinic_environment": forms.Select(attrs={"class": "form-control"}),
        }

        labels = {
            "overall_experience": "Overall",
            "doctor_checkup": "Checkup",
            "staff_behavior": "Behavior",
            "clinic_environment": "Clinic",
        }


class FeedbackRatingForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("appointment", "comment", "overall_experience", "doctor_checkup", "staff_behavior", "clinic_environment")
        widgets = {
            "appointment": forms.HiddenInput(),
            "comment": forms.HiddenInput(),
            "overall_experience": forms.Select(attrs={"class": "form-control w-100 "}),
            "doctor_checkup": forms.Select(attrs={"class": "form-control w-100 "}),
            "staff_behavior": forms.Select(attrs={"class": "form-control w-100 "}),
            "clinic_environment": forms.Select(attrs={"class": "form-control w-100 "}),
        }

        labels = {
            "appointment": "",
            "comment": "",
        }


# class AddMedicalRecordForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         user_id = kwargs.pop("user_id", None)
#         super(AddMedicalRecordForm, self).__init__(*args, **kwargs)

#         if user_id is not None:
#             _doctors = Appointment.objects.filter(
#                 Q(patient__user__id=user_id) & (Q(status="COMPLETED") | Q(status="BOOKED"))
#             )
#             self.fields["doctor"].queryset = Doctor.objects.filter(user__id__in=[x.doctor.user.id for x in _doctors])

#     class Meta:
#         model = MedicalRecords
#         fields = ("title", "doctor", "file")
#         labels = {}
#         widgets = {
#             "title": forms.TextInput(attrs={"class": "form-control"}),
#             "doctor": forms.Select(attrs={"class": "form-control"}),
#             "file": forms.FileInput(attrs={"class": "form-control"}),
#         }

#     def clean_file(self):
#         file = self.cleaned_data.get("file")
#         allowd_extensions = "jpg", "jpeg", "png", "txt", "docx", "pdf"
#         file_ext = str(file).split(".")[-1]
#         if str(file_ext).strip().lower() not in allowd_extensions or file is None:
#             raise forms.ValidationError("Invalid File.")
#         return file


class PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        # super(ChangePasswordForm, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password1"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password2"].widget = forms.PasswordInput(attrs={"class": "form-control"})
