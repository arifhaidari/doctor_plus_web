from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from appointment.models import FeedbackReplies
from .models import SocialMedia
from appointment.models import ApptConditionTreat


class CreateFeedBackRepliesForm(forms.ModelForm):
    class Meta:
        model = FeedbackReplies
        fields = ("feedback", "author", "reply")


class PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        # super(ChangePasswordForm, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password1"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password2"].widget = forms.PasswordInput(attrs={"class": "form-control"})


class SocialMediaForm(forms.ModelForm):
    class Meta:
        model = SocialMedia
        fields = "__all__"
        exclude = ("doctor",)
        labels = {}
        widgets = {
            "whatsapp": forms.TextInput(attrs={"class": "form-control"}),
            "telegram": forms.TextInput(attrs={"class": "form-control"}),
            "facebook": forms.TextInput(attrs={"class": "form-control"}),
            "instagram": forms.TextInput(attrs={"class": "form-control"}),
            "linkedin": forms.TextInput(attrs={"class": "form-control"}),
        }


# add appointment codition thread
class ApptConditionTreatForm(forms.ModelForm):
    class Meta:
        model = ApptConditionTreat
        fields = "__all__"

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "farsi_name": forms.TextInput(attrs={"class": "form-control"}),
            "pashto_name": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "English Name",
            "farsi_name": "Persian Name",
            "pashto_name": "Pashto Name",
        }
