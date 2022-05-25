from django import template
from datetime import date

from doctor.models import Clinic
from ..models import Appointment, DaySchedulePattern, WeekDays
from user.models import Doctor
from django.contrib.auth import get_user_model

User = get_user_model()

register = template.Library()


@register.filter
def filter_by_day(self, args):
    arg_list = [arg for arg in args.split(",")]
    day, user_id = arg_list
    is_doctor = Doctor.objects.filter(user__id=user_id)
    weekday_object = WeekDays.objects.filter(week_day=day)
    if weekday_object.exists() and is_doctor.exists():
        doctor = is_doctor.first()
        weekday = weekday_object.first()
        day_pattern = self.filter(week_day=weekday, doctor=doctor)
        if day_pattern.exists():
            pattern = day_pattern.first()
            if pattern.active:
                return True
    return False


@register.filter
def filter_by_status(self, user):
    if self.patient == user.patient and self.status == Appointment.ApptStatus.BOOKED:
        return False
    return True


# for reschedule appointments
@register.filter
def booked_for_relative(self, user):
    return True if self.relative else False


@register.filter
def filter_by_pattern(self, args):
    today_date = date.today()
    doctor = self.first().doctor
    arg_list = [arg for arg in args.split(",")]
    day, clinic_id = arg_list
    is_clinic = Clinic.objects.filter(id=clinic_id)
    weekday_object = WeekDays.objects.filter(week_day=day)
    if weekday_object.exists() and is_clinic.exists():
        clinic = is_clinic.first()
        weekday = weekday_object.first()
        day_pattern = DaySchedulePattern.objects.filter(week_day=weekday, clinic=clinic, doctor=doctor)
        if day_pattern.exists():
            pattern = day_pattern.first()
            filtered_appt_list = self.filter(day_pattern=pattern, clinic=clinic, appt_date__gte=today_date)
            if filtered_appt_list.exists():
                return filtered_appt_list
    return None


@register.filter
def day_schedule_filter(self, args):
    is_daypattern_exist = self.filter(doctor=args)
    if is_daypattern_exist.exists():
        return is_daypattern_exist
    return None


# register.filter('filter_by_day', filter_by_day)
