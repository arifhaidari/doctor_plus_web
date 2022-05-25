from django import forms
from .models import AppointmentConditionThread


class AddAppointmentCoditionThreadForm(forms.ModelForm):
    class Meta:
        model = AppointmentConditionThread
        fields = ("name", "farsi_name", "pashto_name")
