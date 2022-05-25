from datetime import timedelta, datetime, date
from django.utils import timezone
import random
from dateutil.relativedelta import relativedelta
from django.template.defaultfilters import slugify
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.dispatch import receiver

from . import validators as valid

# from appointment.models import Feedback as fd

# from django.core.mail import send_mail
# from django.template.loader import get_template
# from django.utils import timezone


def upload_speciality_icon(instance, filename):
    return "speciality_icon/{filename}".format(filename=filename)


def upload_user_avatar(instance, filename):
    if instance.user_type == User.Types.Doctor:
        return "user_avatar/doctors/{name}_{filename}".format(name=slugify(instance), filename=filename)
    elif instance.user_type == User.Types.Patient:
        return "user_avatar/patients/{name}_{filename}".format(name=slugify(instance), filename=filename)
    elif instance.user_type == User.Types.Relative:
        return "user_avatar/relative/{name}_{filename}".format(name=slugify(instance), filename=filename)
    elif instance.user_type == User.Types.Admin:
        return "user_avatar/admin/{name}_{filename}".format(name=slugify(instance), filename=filename)
    elif instance.user_type == User.Types.Blogger:
        return "user_avatar/blogger/{name}_{filename}".format(name=slugify(instance), filename=filename)
    elif instance.user_type == User.Types.HealthMinistry:
        return "user_avatar/HealthMinistry/{name}_{filename}".format(name=slugify(instance), filename=filename)
    else:
        return "user_avatar/unknow_category/{name}_{filename}".format(name=slugify(instance), filename=filename)


class UserManager(BaseUserManager):
    def create_user(
        self,
        phone,
        full_name=None,
        rtl_full_name=None,
        password=None,
        gender = 'Male',
        user_type = 'Patient',
        is_active=False,
        is_staff=False,
        is_admin=False,
    ):
        try:
            if not phone:
                    raise ValueError("Users must have an phone number")
            if not password:
                raise ValueError("Users must have a password")
            # user_obj = None
            if is_admin == False:
                user_obj = self.model(phone=phone, full_name=full_name, rtl_full_name=rtl_full_name, gender=gender, user_type=user_type)
            else:
                user_obj = self.model(phone=phone, gender=gender, user_type='Admin')
            user_obj.set_password(password)  # change user password
            user_obj.staff = is_staff
            user_obj.admin = is_admin
            user_obj.active = is_active
            user_obj.save(using=self._db)
        except Exception as e:
            print('value fo e000000')
            print(e)
            user_obj = None
        return user_obj

    def create_staffuser(self, phone, password=None):
        user = self.create_user(phone=phone, password=password, is_staff=True)
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(phone=phone, password=password, is_staff=True, is_admin=True)
        return user


class User(AbstractBaseUser):
    GENDER = (("Male", "Male"), ("Female", "Female"), ("Other", "Other"))

    class Types(models.TextChoices):
        Patient = "Patient"
        Doctor = "Doctor"
        Relative = "Relative"
        Admin = "Admin"
        Blogger = "Blogger"
        HealthMinistry = "HealthMinistry"
        AdminPlus = "AdminPlus"

    user_type = models.CharField(max_length=50, choices=Types.choices, default=Types.Patient)
    full_name = models.CharField(max_length=255, blank=True, null=True, validators=[valid.name])
    rtl_full_name = models.CharField(max_length=255, blank=True, null=True)
    # phone = models.CharField(max_length=255, unique=True, validators=[valid.phone_number])
    phone = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.CharField(max_length=255, blank=True, null=True, unique=True, validators=[valid.email])
    date_of_birth = models.DateField(null=True, blank=True, validators=[valid.dob])
    avatar = models.ImageField(
        upload_to=upload_user_avatar, null=True, blank=True,
        # default="user_avatar/default_avatar3.png",
        validators=[valid.avatar_size, valid.avatar_type],
    )
    active = models.BooleanField(default=False)
    suspend = models.BooleanField(default=False)
    gender = models.CharField(max_length=15, choices=GENDER, default="Male")
    admin = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    # username = models.CharField(max_length=64, null=True, blank=True)

    USERNAME_FIELD = "phone"  # username
    # USERNAME_FIELD and password are required by default
    REQUIRED_FIELDS = []  # ['full_name'] # it is for python manage.py createsuperuser

    objects = UserManager()

    def __str__(self):
        if self.full_name:
            return self.full_name
        elif self.phone:
            return self.phone
        elif self.email:
            return self.email
        return "Name Unknown"

    def delete(self, *args, **kwargs):
        self.avatar.delete()
        super().delete(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # self.type = User.Types.PATIENT
    #     # do some other editing after saving
    #     print("------>> saveing model of the user ", self.phone)
    #     return super().save(*args, **kwargs)

    def get_full_name(self):
        return self.full_name or self.rtl_full_name or self.phone

    def string_birth_date(self):
        return str(self.date_of_birth) or ""

    def user_age(self):
        today = date.today()
        if self.date_of_birth:
            return str(
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return ""

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # added by ali
    def has_perms(self, perm, obj=None):
        return True

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    # def get_absolute_url(self):
    #     return reverse("dashboard:detail", kwargs={"id": self.id})


class OTPVerification(models.Model):
    phone = models.CharField(max_length=120)
    six_digit = models.CharField(max_length=10, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.phone} - {self.timestamp}" or "otp_object"
def uniqu_six_digit_generator():
    the_random = random.randint(100000, 999999)
    is_random = OTPVerification.objects.filter(six_digit=the_random)
    if is_random.exists():
        uniqu_six_digit_generator()
    else:
        return str(the_random)

@receiver(pre_save, sender=OTPVerification)
def set_the_time(sender, instance, *args, **kwargs):
    instance.six_digit = uniqu_six_digit_generator()
    # we can send to user cellphone form here as well
    instance.timestamp = timezone.now() + timedelta(hours=4, minutes=30)

class DoctorTitle(models.Model):
    title = models.CharField(max_length=120)
    farsi_title = models.CharField(max_length=120)
    pashto_title = models.CharField(max_length=120)

    def __str__(self):
        return self.title or "doctor_title_object"


class SpecialityCategory(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    farsi_name = models.CharField(max_length=255, null=True, blank=True)
    pashto_name = models.CharField(max_length=255, null=True, blank=True)
    icon = models.ImageField(upload_to=upload_speciality_icon, null=True, blank=True)

    def __str__(self):
        return self.name or self.farsi_name or self.pashto_name or ""


class BloodGroup(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


def speciality_icons_upload_to(instance, filename):
    return f"speciality/{instance.speciality_category}/{filename}/"


class Speciality(models.Model):
    class Meta:
        verbose_name = "Speciality"
        verbose_name_plural = "Specialities"

    name = models.CharField(max_length=256)
    farsi_name = models.CharField(max_length=256, null=True, blank=True)
    pashto_name = models.CharField(max_length=256, null=True, blank=True)
    speciality_category = models.ForeignKey(SpecialityCategory, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class Condition(models.Model):
    speciality = models.ForeignKey("Speciality", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    farsi_name = models.CharField(max_length=128)
    pashto_name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.name)


class Service(models.Model):
    speciality = models.ForeignKey("Speciality", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    farsi_name = models.CharField(max_length=128)
    pashto_name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.name)


class Doctor(models.Model):
    class DoctorType(models.TextChoices):
        Volenteer = "Volunteer"
        Onpremise = "Onpremise"
        Onlineconsultant = "Onlinecunsultant"

    # PROFESSIONAL_STATUS = (0, "None"), (1, "Pending"), (2, "Active")
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="doctor")
    doctor_type = models.CharField(max_length=50, choices=DoctorType.choices, default=DoctorType.Volenteer)
    title = models.ForeignKey(DoctorTitle, on_delete=models.CASCADE, null=True, blank=True)
    speciality = models.ManyToManyField(Speciality, blank=True)
    service = models.ManyToManyField(Service, blank=True)
    condition = models.ManyToManyField(Condition, blank=True)
    doc_license_no = models.CharField(max_length=150, unique=True, null=True, blank=True)
    # fee = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True)
    fee = models.IntegerField(null=True, blank=True)
    is_free_service = models.BooleanField(default=False)
    bio = models.TextField(null=True, blank=True)
    farsi_bio = models.TextField(null=True, blank=True)
    pashto_bio = models.TextField(null=True, blank=True)
    # professional_status = models.PositiveSmallIntegerField(choices=PROFESSIONAL_STATUS, default=0)
    professional_status = models.BooleanField(default=False)
    is_profile_on_progress = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} {self.user.full_name}"

    def speciality_cats(self):
        return list(set([x.speciality_category.name for x in self.speciality.all()]))

    def specialities(self):
        return list(set(x.name for x in self.speciality.all()))

    clinicz = lambda self: [x.id for x in self.clinic_set.exclude(created_by__user=self.user)]
    mclinicz = lambda self: [x.id for x in self.clinic_set.filter(created_by__user=self.user)]

    @property
    def total_xp(self):
        xp_start_date = min([xp.experience_start_date() for xp in self.experience_set.all()]).split("-")
        d0 = date(int(xp_start_date[0]), int(xp_start_date[1]), int(xp_start_date[2]))
        d1 = datetime.now().date()
        return f"{relativedelta(d1, d0).years} years, {relativedelta(d1, d0).years} months"


class FreeServiceSchedule(models.Model):
    doctor = models.OneToOneField("Doctor", on_delete=models.CASCADE, primary_key=True)
    start_at = models.DateField()
    end_at = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.doctor and self.start_at and self.end_at:
            return "doctor: {}, start: {}, end: {}".format(self.doctor, self.start_at, self.end_at)
        return "Unknown Object"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="patient")
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE, null=True, blank=True)
    share_record_to_all = models.BooleanField(default=True)
    
        

    def __str__(self):
        return self.user.full_name or self.user.rtl_full_name


class RelativeRelation(models.Model):
    relation = models.CharField(max_length=16)
    farsi_relation = models.CharField(max_length=32, null=True)
    pashto_relation = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.relation or self.farsi_relation


class Relative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="relative")
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE, null=True, blank=True)
    relation = models.ForeignKey(RelativeRelation, on_delete=models.CASCADE, null=True)
    share_record_to_all = models.BooleanField(default=True)

    def __str__(self):
        return self.user.full_name or self.user.rtl_full_name or self.user.phone

    def get_patient(self):
        return self.patient


class Blogger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.full_name or self.user.rtl_full_name or self.user.phone


class HealthMinistry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.full_name or self.user.rtl_full_name or self.user.phone


# this is for calling the reciever
from django.urls import reverse
from django.core.mail import send_mail  
from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )