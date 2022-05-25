from django import template
from user.models import Patient
from appointment.models import Appointment, Feedback
from django.db.models import Q

register = template.Library()


@register.filter
def split_by(text, word=4):
    return " ".join(text.split()[:word])


# doctor
@register.inclusion_tag("adminplus/components/doctor_rating.html")
def doctor_rating(doctor):
    doc_apps = doctor.appointment_set.filter(
        Q(feedback_status=True) & (Q(relative__isnull=False) | Q(patient__isnull=False))
    )
    stars = [x.good_count for x in Feedback.objects.filter(appointment__in=list(doc_apps))]
    star_av = 0 if len(stars) == 0 else (sum(stars) * 25) / (len(stars) * 10)
    return {"star_av": star_av, "doctor": doctor}


# patient
@register.simple_tag
def patient_last_compeleted_appointment(patient):
    last_app = Appointment.objects.filter(
        patient=patient, relative__isnull=True, status=Appointment.ApptStatus.COMPLETED
    ).last()
    if last_app:
        return f"{last_app.appt_date} - {last_app.doctor}"
    return " "


# @register.simple_tag
# def patient_paid_for_appointment(patient):
#     last_app = Appointment.objects.filter(
#         patient=patient, relative__isnull=True, status=Appointment.ApptStatus.COMPLETED
#     ).last()
#     if last_app:
#         return last_app.doctor.fee
#     return "0"
