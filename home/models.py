from django.db import models
from django.contrib.auth import get_user_model
from user.models import Doctor, Patient

User = get_user_model()


class Language(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)
    rtl_name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.name or self.rtl_name or ""


class CityQuerySet(models.query.QuerySet):
    def serialize(self):
        return self.values("id", "name", "rtl_name")

    # return {
    #        'id': self.pk,
    #        'name': self.name,
    #        'rtl_name': self.rtl_name,
    #      #   'name': " ".join((self.user.first_name, self.user.last_name)),
    #      #   'birthday': self.birth.strftime("%d %M, %Y"),
    #      }


class CityManager(models.Manager):
    def get_queryset(self):
        return CityQuerySet(self.model, using=self._db)

    def serialize(self):
        return self.get_queryset().serialize()


class City(models.Model):
    name = models.CharField(max_length=200)
    rtl_name = models.CharField(max_length=200)

    objects = CityManager()

    def __str__(self):
        return str(self.name) or 'city_object'

    def with_rtl_name(self):
        return f"{self.name} - {self.rtl_name}"

    # def serialize(self):
    # return {
    #   'id': self.pk,
    #   'name': self.name,
    #   'rtl_name': self.rtl_name,
    # #   'name': " ".join((self.user.first_name, self.user.last_name)),
    # #   'birthday': self.birth.strftime("%d %M, %Y"),
    # }


class District(models.Model):
    name = models.CharField(max_length=200)
    rtl_name = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or 'district_object'

    def with_rtl_name(self):
        return f"{self.name} - {self.rtl_name}"


class Payment(models.Model):
    received_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    pay_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return (self.amount) or ""


class SocialMedia(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name or ""


class DoctorSocialMedia(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor_name")
    social_media = models.ForeignKey(SocialMedia, on_delete=models.CASCADE, null=True, blank=True)
    social_media_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.social_media or self.doctor


class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="address")
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        # return "address object" # given the below casting because of the error
        return str(self.city) or str(self.district) or "address_object"
