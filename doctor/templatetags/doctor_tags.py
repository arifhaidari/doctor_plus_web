from django import template
from django.db.models import Q, Count
from DoctorPlus.utils import star_out_of_five
from appointment.models import Feedback, Appointment  # , DaySchedulePattern
from patient.models import FavoriteDoctor
from notification.models import Notification
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from chat.models import ChatMessage, Thread

from operator import itemgetter

from ..models import Doctor

register = template.Library()


@register.inclusion_tag("doctor/templatetag_files/doctor_rating.html")
def doctor_rating(doctor):
    average_star, feedback_no = star_out_of_five(doctor)
    print('value of average_star')
    print(average_star)
    return {"average_star": average_star, "feedback_no": feedback_no, "doctor": doctor}

@register.inclusion_tag("doctor/templatetag_files/appt_feedback.html")
def appt_feedback(score_count):
    return {"score_count": score_count}

@register.simple_tag
def is_your_fav_dcotor(doctor, patient):
    return bool(FavoriteDoctor.objects.filter(patient=patient, doctor=doctor))


@register.filter
def split_by_words_f(text, count=2):
    return " ".join(text.split()[:count]) + ".."


#  notifications
@register.simple_tag
def got_feedback(appointment_id):
    feedback = get_object_or_404(Feedback, appointment__id=appointment_id)
    return f"/doctor/review/{feedback.id}"


@register.simple_tag
def total_notifications(doctor__user):
    notifications = Notification.objects.filter(receiver=doctor__user, seen=False).count()
    return notifications


@register.simple_tag
def total_chat_notifications(doctor__user):
    the_filter = Q(Q(thread__second=doctor__user) & ~Q(thread__first=doctor__user) & Q(seen=False))
    chat_queryset = ChatMessage.objects.filter(the_filter).distinct().count()
    return chat_queryset

# chat
@register.simple_tag
def doctor_last_chat(user):
    # seen all notification
    the_filter = Q(Q(thread__second=user) & ~Q(thread__first=user) & Q(seen=False))
    ChatMessage.objects.filter(the_filter).update(seen=True)
    # find last chat
    thread = Thread.objects.filter(Q(first=user) | Q(second=user)).last()
    if not thread:
        print('is thread is none')
        completed_app = Appointment.objects.filter(Q(status="COMPLETED") & Q(doctor__user=user) & Q(relative=None)).last()
        if not completed_app:
            # print("you dont have any chat options")
            return HttpResponseNotFound()
        thread = Thread.objects.create(first=user, second=completed_app.doctor.user)

    if thread.first == user:
        return f"/chat/{thread.second.phone}/"
    else:
        return f"/chat/{thread.first.phone}/"


# public profile clinic related dayschedulepattern
@register.filter
def doctor_related_dayschedulepattern(days, doctor):
    return days.filter(doctor=doctor)


# home page
@register.filter
def top_rated_doctors(args=None):
    top_doctors = Doctor.objects.filter(professional_status=True).annotate(
    num_appts=Count('appointment', filter=Q(appointment__status=Appointment.ApptStatus.COMPLETED))
    ).order_by('-num_appts')[:10]
    return top_doctors
