from django.db import models
from django.contrib.auth import get_user_model
from chat.validators import attachment_valid_size, attachment_valid_type
from user.models import Relative, Doctor, Patient
from home.models import City, District

User = get_user_model()


def upload_record_doc(instance, filename):
    return "medical_doc/{user}/{filename}/".format(user=instance.user, filename=filename)

class FavoriteDoctor(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    doctor = models.ManyToManyField(Doctor, blank=True)

    def __str__(self):
        return str(self.patient) or ""


class VerifyPhone(models.Model):
    phone_number = models.CharField(max_length=20)
    verification_token = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.phone_number or ""
