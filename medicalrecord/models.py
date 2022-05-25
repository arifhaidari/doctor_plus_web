from typing import Generator
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, m2m_changed
from .validators import attachment_valid_size, attachment_valid_type

# from .validators import attachment_valid_size, attachment_valid_type
def upload_file_path(instance, filename):
    return f"medicalrecord/file-sharing/user_{instance.medical_record.patient.user.id}/{filename}"


class MedicalRecordFile(models.Model):
    class Meta:
        verbose_name = "Medical Record File"
        verbose_name_plural = "Medical Record Files"
    medical_record = models.ForeignKey('MedicalRecords', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_file_path, validators=[attachment_valid_size, attachment_valid_type])

class MedicalRecords(models.Model):
    class Meta:
        verbose_name = "Medical Record"
        verbose_name_plural = "Medical Records"

    # patient = models.ForeignKey("FileSharingPatient", on_delete=models.CASCADE)
    patient = models.ForeignKey("user.Patient", on_delete=models.CASCADE)
    relative = models.ForeignKey("user.relative", on_delete=models.CASCADE, blank=True, null=True)
    related_doctor = models.ForeignKey('user.Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_doctor')
    shared_with = models.ManyToManyField('user.Doctor', blank=True)
    title = models.CharField("Title", max_length=255, null=True, blank=True)
    # doctor_access = models.BooleanField("Doctor", default=True)
    general_access = models.BooleanField("General", default=True)
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or 'medical record object'
        # return f"{self.patient} | {self.related_doctor}"

    def file_name(self):
        return self.file.name.split("/")[-1]

    @property
    def relative_or_self(self):
        return self.relative or self.patient

# @receiver(m2m_changed, sender=MedicalRecords.shared_with.through)
# def add_related_to_shared_with(sender, instance, action, *args, **kwargs):
#     print('iside the many to many change ')
    # insance is the MedicalRecords
    # model the related field in many to many 
    # action is the pre_save and post_save 
    # kwargs.get('object') is the model of the many to many


# there is a different signal for many to many relationship
# @receiver(post_save, sender=MedicalRecords)
# def add_to_share_with(sender, instance, created, *args, **kwargs):
#     print('value fo created')
#     print('value fo instance.shared_with')
#     print(instance.shared_with)
#     print(created)
#     if created:
#         Klass = instance.__class__
#         is_exist = Klass.objects.filter(shared_with=instance.related_doctor, id=instance.id).exists()
#         print('value of is_exist')
#         print(is_exist)
#         print(Klass)
#         print(instance)
#         print(instance.related_doctor)
#         print(instance.id)
#         if not is_exist:
#             try:
#                 instance.shared_with.add(instance.related_doctor)
#                 print('after adding to it back')
#             except Exception as e:
#                 print('value fo error')
#                 print(e)

