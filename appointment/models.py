from pyexpat import model
from django.db import models
from doctor.models import Clinic
from datetime import date
from django.shortcuts import redirect
from django.contrib import messages
import calendar
from datetime import timedelta
from django.db.models import Q
from django.contrib.auth import get_user_model
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

from notification import notification_manager as notification_manager

User = get_user_model()

# def upload_qr_image(instance, filename):
#     if instance:
#         return "appt_qr/{name}_{filename}/".format(name=slugify(instance), filename=filename)


class WeekDays(models.Model):
    week_day = models.CharField(max_length=120, null=True, blank=True)
    rtl_week_day = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.week_day or self.rtl_week_day or ""


# Days of the week policy # Pattern
class DaySchedulePattern(models.Model):
    week_day = models.ForeignKey(WeekDays, on_delete=models.CASCADE, null=True, blank=True)
    time_slot_duration = models.DurationField(null=True, blank=True)
    start_day_time = models.DurationField(null=True, blank=True)
    end_day_time = models.DurationField(null=True, blank=True)
    doctor = models.ForeignKey("user.Doctor", on_delete=models.CASCADE, null=True, blank=True, related_name="scheduled_by")
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.week_day}- {self.clinic} - {self.doctor}"
        return self.week_day.__str__()

    def is_every_day_pattern(self):
        doctor, clinic = self.doctor, self.clinic
        for day in DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic):
            if not (
                day.time_slot_duration == self.time_slot_duration
                and day.start_day_time == self.start_day_time
                and day.end_day_time == self.end_day_time
            ):
                return False
        return True

    # for api
    def total_booked_appt_no(self):
        qs = Appointment.objects.filter(Q(day_pattern__id=self.id) & ~Q(status=Appointment.ApptStatus.COMPLETED))
        return qs.count()

class ApptConditionTreat(models.Model):
    # class Meta:
        # verbose_name = "Condition Thread"
        # verbose_name_plural = "Condition Threads"

    name = models.CharField(max_length=64, unique=True)
    farsi_name = models.CharField(max_length=128, blank=True, null=True)
    pashto_name = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name or self.farsi_name or self.pashto_name

    def clean(self):
        self.name = self.name.strip().capitalize()


class AppointmentQuerySet(models.QuerySet):
    def schedule_by_pattern(self, doctor, clinic, request, operation):
        deactivated_slots = DeactivatedApptSlot.objects.filter(doctor=doctor, clinic=clinic)
        if operation == "manual" and deactivated_slots.exists():
            deactivated_slots.delete()
        today_date = date.today()
        week_day_pattern = DaySchedulePattern.objects.filter(doctor=doctor, clinic=clinic)
        
        if week_day_pattern.exists():
            # print('valuer of Refresh your page and submit your schedule data for a clinic, looks like some of your clinic has no time schedule')
            # 351_tackle
            # this reidrect create some error sometimes 
        #     messages.warning(request, "Refresh your page and submit your schedule data for a clinic, looks like some of your clinic has no time schedule")
        #     return redirect("appointment:schedule")
        # else:
            for pattern in week_day_pattern:
                if pattern.active:
                    schedule_by_a_pattern(self, pattern, today_date, clinic, doctor, operation, deactivated_slots)


def schedule_by_a_pattern(self, pattern, today_date, clinic, doctor, operation, deactivated_slots=None):
    pattern_appt_object = self.filter(
        day_pattern=pattern, appt_date__gte=today_date, clinic=clinic, doctor=doctor
        ).filter(~Q(status=Appointment.ApptStatus.COMPLETED))
    if operation == "manual":
        is_patient_book_to_pattern = pattern_appt_object.filter(~Q(patient=None) | ~Q(relative=None) & Q(status=Appointment.ApptStatus.BOOKED))
        if is_patient_book_to_pattern.exists():
            for patr_obj in is_patient_book_to_pattern:
                notification_manager.appt_canceled_by_doctor(patr_obj)

        pattern_appt_object.delete()
        slot_time_by_pattern(self, pattern, operation, doctor, clinic, today_date)
    else:
        if not pattern_appt_object.exists():
            slot_time_by_pattern(self, pattern, operation, doctor, clinic, today_date, deactivated_slots)


def slot_time_by_pattern(self, pattern, operation, doctor, clinic, today_date, deactivated_slots=None):
    start_temp_time = pattern.start_day_time
    while start_temp_time <= pattern.end_day_time:
        if operation != "manual":
            if (
                deactivated_slots.exists()
                and deactivated_slots.filter(start_appt_time=start_temp_time, day_pattern=pattern).exists()
            ):
                create_by_pattern(self, pattern, doctor, clinic, start_temp_time, False, today_date)
            else:
                create_by_pattern(self, pattern, doctor, clinic, start_temp_time, True, today_date)
        else:
            create_by_pattern(self, pattern, doctor, clinic, start_temp_time, True, today_date)
        start_temp_time += pattern.time_slot_duration
        break_the_loop = pattern.end_day_time - start_temp_time
        if break_the_loop < pattern.time_slot_duration:
            break


def create_by_pattern(self, pattern, doctor, clinic, start_temp_time, active_bool, today_date):
    today_week_day = str(calendar.day_name[today_date.weekday()])
    pattern_week_day = str(pattern.week_day)
    flag = True
    appt_date_object = today_date
    if today_week_day != pattern_week_day:
        while flag:
            appt_date_object += timedelta(days=1)
            if str(calendar.day_name[appt_date_object.weekday()]) == pattern_week_day:
                flag = False
    self.create(
        doctor=doctor,
        clinic=clinic,
        day_pattern=pattern,
        start_appt_time=start_temp_time,
        end_appt_time=start_temp_time + pattern.time_slot_duration,
        appt_date=appt_date_object,
        active=active_bool,
    )


class AppointmentManager(models.Manager):
    def get_queryset(self):
        return AppointmentQuerySet(self.model, using=self._db)

    def clear_history(self):
        today_date = date.today()
        appt_status = Appointment.ApptStatus
        object_list = self.filter(
            appt_date__lt=today_date,
        ).exclude(status=appt_status.COMPLETED)
        # ).exclude(Q(status=appt_status.COMPLETED) | Q(status=appt_status.EXPIRED))
        if object_list.exists():
            object_list.delete()

    def filter_by_clinic(self, clinic):
        return self.filter(clinic=clinic)

    def schedule_by_pattern(self, doctor, clinic, request, operation):
        return self.get_queryset().schedule_by_pattern(doctor, clinic, request, operation)


class Appointment(models.Model):
    class ApptStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        BOOKED = "BOOKED", "Booked"
        EXPIRED = "EXPIRED", "Expired"
        COMPLETED = "COMPLETED", "Completed"
        PATIENT_CANCELED = "PATIENT_CANCELED", "Patient_Canceled"
        DOCTOR_CANCELED = "DOCTOR_CANCELED", "Doctor_Canceled"

    doctor = models.ForeignKey("user.Doctor", on_delete=models.CASCADE)
    patient = models.ForeignKey("user.Patient", on_delete=models.CASCADE, null=True, blank=True)
    relative = models.ForeignKey("user.Relative", on_delete=models.CASCADE, null=True, blank=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True)
    day_pattern = models.ForeignKey(DaySchedulePattern, on_delete=models.SET_NULL, null=True, blank=True)
    start_appt_time = models.DurationField(null=True, blank=True)
    end_appt_time = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=ApptStatus.choices, default=ApptStatus.PENDING)
    feedback_status = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    appt_date = models.DateField(null=True, blank=True)
    booked_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    # rescheduled_at = models.DateTimeField(auto_now=True)
    condition_treated = models.ManyToManyField(ApptConditionTreat, blank=True)
    remark = models.TextField(null=True, blank=True)

    objects = AppointmentManager()

    # using this method occures the error of: maximum recursion depth exceeded
    # def __str__(self):
    #      if self.patient or self.relative:
    #           return "Duration: {}, Patient: {}".format(self.appt_duration, self.patient or self.relative)
    #      return "Duration: {}, Doctor: {}".format(self.appt_duration, self.doctor) or ""

    # def __str_(self):
    #     return self.start_appt_time or f"{self.patient} | {self.doctor}" or ""

    def __str__(self):
        return str(self.id)
        # return f"{self.doctor.user} - {self.patient} - {self.relative}" or 'appt_object'

    def appt_duration(self):
        if self.start_appt_time and self.end_appt_time:
            return str(self.end_appt_time - self.start_appt_time)
        return ""


class DeactivatedApptSlot(models.Model):
    doctor = models.ForeignKey("user.Doctor", on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    day_pattern = models.ForeignKey(DaySchedulePattern, on_delete=models.CASCADE, null=True, blank=True)
    start_appt_time = models.DurationField(null=True, blank=True)
    end_appt_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        if self.start_appt_time and self.end_appt_time:
            return "Start Time Slot: {}, End Time Slot: {}".format(self.start_appt_time, self.end_appt_time)
        return "Unknown Object"


class ApptQrCode(models.Model):
    class Meta:
        verbose_name = "Appointment Qr Code"
        verbose_name_plural = "Appointments Qr Code"

    appt_slot = models.ForeignKey("Appointment", on_delete=models.CASCADE, related_name="qrcode")
    qr_code_img = models.ImageField(upload_to="appt_qr", null=True, blank=True)

    __str__ = lambda self: f"QrCode_of_appointment_{self.appt_slot.id}"

    def save(self, *args, **kwargs):
        # qr_code_string = qrcode.make(f'{self.doctor}_{self.booked_by_patient_or_relative}_{self.clinic}_{str(self.appt_slot.id)}')
        if not self.pk:
            qr_code_string = qrcode.make(str(self.appt_slot.id))
            qr_canvas = Image.new("RGB", (290, 290), "white")
            ImageDraw.Draw(qr_canvas)
            qr_canvas.paste(qr_code_string)
            # qr_img_name = f"appt_qr_{self.doctor}_{str(self.appt_slot.id)}.png"
            qr_img_name = f"{self.appt_slot.doctor}_{str(self.appt_slot.id)}.png"
            buffer_object = BytesIO()
            qr_canvas.save(buffer_object, "PNG")
            self.qr_code_img.save(qr_img_name, File(buffer_object), save=False)
            qr_canvas.close()
            super().save(*args, **kwargs)

    # def booked_by_patient_or_relative(self):
    #     if self.patient or self.relative:
    #         return self.patient or self.relative
    #     return ""


class Feedback(models.Model):
    class Meta:
        verbose_name = "Appoinment Feedback"
        verbose_name_plural = "Appointments Feedback"

    class FeedbackOption(models.TextChoices):
        Good = "Good"
        Better = "Better"

    # doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True, related_name="doctor_id")
    # patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True, related_name="patient_id")
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="feedback")
    comment = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    overall_experience = models.CharField(max_length=32, choices=FeedbackOption.choices, default=FeedbackOption.Good)
    doctor_checkup = models.CharField(max_length=32, choices=FeedbackOption.choices, default=FeedbackOption.Good)
    staff_behavior = models.CharField(max_length=32, choices=FeedbackOption.choices, default=FeedbackOption.Good)
    clinic_environment = models.CharField(max_length=32, choices=FeedbackOption.choices, default=FeedbackOption.Good)
    # is_patient_submit = models.BooleanField(default=False) # might not be needed 

    def __str__(self):
        return self.comment or str(self.id) or "feedback_object"

    @property
    def score_count(self):
        counter = 1
        for f in ["overall_experience", "doctor_checkup", "staff_behavior", "clinic_environment"]:
            if getattr(self, f) == "Better":
                counter += 1
        if counter == 1:
            counter += 2;
        elif counter == 2:
            counter += 1.5;
        elif counter == 3:
            counter += 1;
        elif counter == 4:
            counter += 0.5;
        return counter


    @property
    def good_count(self):
        counter = 0
        for f in ["overall_experience", "doctor_checkup", "staff_behavior", "clinic_environment"]:
            if getattr(self, f) == "Good":
                counter += 1
        return counter
    
    @property
    def better_count(self):
        counter = 1
        for f in ["overall_experience", "doctor_checkup", "staff_behavior", "clinic_environment"]:
            if getattr(self, f) == "Better":
                counter += 1
        return counter


class FeedbackReplies(models.Model):
    class Meta:
        verbose_name = "Feedback Reply"
        verbose_name_plural = "Feedback Replies"

    feedback = models.ForeignKey("Feedback", on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey("user.User", on_delete=models.CASCADE)
    reply = models.CharField(max_length=512, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)



