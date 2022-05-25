from django.db import models
from django.contrib.auth import get_user_model
from user.models import Doctor, Speciality, Patient
from home.models import City, District

User = get_user_model()


def upload_docs_file(instance, filename):
    return "doctor_docs/user_{user.id}/{filename}/".format(user=instance.user, filename=filename)


# control the uploading file ... the size and format as well
class DoctorAttachment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_docs_file)

    def __str__(self):
        return str(self.doctor.user)


class ClinicQuerySet(models.QuerySet):
    # maybe require a doctor object
    def deactivated_clinics(self):
        return self.filter(active=False)


class ClinicManager(models.Manager):
    def get_queryset(self):
        return ClinicQuerySet(self.model, using=self._db)

    def activated_clinics(self):
        return self.filter(active=True)

    def deactivated_clinics(self):
        return self.get_queryset().deactivated_clinics()


class Clinic(models.Model):
    clinic_name = models.CharField(max_length=255)
    rtl_clinic_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    rtl_address = models.CharField(max_length=255, null=True, blank=True)
    doctor = models.ManyToManyField(Doctor, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longtitude = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, related_name="created_by", null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ClinicManager()

    def __str__(self):
        return self.clinic_name

    def clean(self):
        self.clinic_name = self.clinic_name.strip().capitalize()
        self.rtl_clinic_name = self.rtl_clinic_name.strip().capitalize()

    @property
    def total_doctor(self):
        return str(self.doctor.all().count())


class DegreeType(models.Model):
    name = models.CharField(max_length=255)
    farsi_name = models.CharField(max_length=255)
    pashto_name = models.CharField(max_length=255)
    
    def __str__(self):
        if self.name and self.farsi_name:
            return "{} - {}".format(self.name, self.farsi_name)
        return ""

class EducationDegree(models.Model):
    # class DegreeType(models.TextChoices):
    #     Bachelor = "Bachelor"
    #     Master = "Master"
    #     Diploma = "Diploma"
    #     Nonclinical = "Nonclinical"
    
    name = models.CharField(max_length=255, null=True, blank=True)
    farsi_name = models.CharField(max_length=255, null=True, blank=True)
    pashto_name = models.CharField(max_length=255, null=True, blank=True)
    degree_type = models.ForeignKey(DegreeType, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.name or self.farsi_name or ""
    
    

class Education(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=255, null=True, blank=True)
    rtl_school_name = models.CharField(max_length=255, null=True, blank=True)
    degree = models.ForeignKey("EducationDegree", on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.school_name or self.rtl_school_name or ""

    def string_start_date(self):
        if self.start_date:
            return str(self.start_date)
        return ""

    def string_end_date(self):
        if self.end_date:
            return str(self.end_date)
        return ""



class Award(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    award_name = models.CharField(max_length=255, null=True, blank=True)
    rtl_award_name = models.CharField(max_length=255, null=True, blank=True)
    award_year = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.award_name or self.rtl_award_name or ""

    def string_award_year(self):
        if self.award_year:
            return str(self.award_year)
        return ""


class Experience(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=255, null=True, blank=True)
    rtl_hospital_name = models.CharField(max_length=255, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    rtl_designation = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.hospital_name or self.rtl_hospital_name or ""

    def experience_start_date(self):
        if self.start_date:
            return str(self.start_date)
        return ""

    def experience_end_date(self):
        if self.end_date:
            return str(self.end_date)
        return ""


class DoctorProfileView(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    counter = models.PositiveIntegerField(default=0)
    datestamp = models.DateField(auto_now=True)

    def __str__(self):
        return "{}, Profile View: {}".format(self.doctor, self.counter)


class SocialMedia(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    whatsapp = models.CharField(max_length=255, null=True, blank=True)
    telegram = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.doctor) or self.facebook or ""


class MedicalCondition(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    farsi_name = models.CharField(max_length=255, null=True, blank=True)
    pashto_name = models.CharField(max_length=255, null=True, blank=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name or self.farsi_name or self.pashto_name or ""


class Disease(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    farsi_name = models.CharField(max_length=255, null=True, blank=True)
    pashto_name = models.CharField(max_length=255, null=True, blank=True)
    speciality = models.ManyToManyField(Speciality, related_name="disease")

    def __str__(self):
        return self.name or self.farsi_name or self.pashto_name or ""


class Symptoms(models.Model):
    class Meta:
        verbose_name = "Symptom"
        verbose_name_plural = "Symptoms"

    name = models.CharField(max_length=255, null=True, blank=True)
    farsi_name = models.CharField(max_length=255, null=True, blank=True)
    pashto_name = models.CharField(max_length=255, null=True, blank=True)
    disease = models.ManyToManyField(Disease, related_name="symptom")

    def __str__(self):
        return self.name or self.farsi_name or self.pashto_name or ""
