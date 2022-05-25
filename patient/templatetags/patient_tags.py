from posixpath import split
from django import template
from django.db.models import Q
from django.http import HttpResponseNotFound
from appointment.models import Appointment
from chat.models import ChatMessage, Thread
from notification.models import Notification

# from patient.models import Notification
register = template.Library()

@register.simple_tag
def patiet_last_chat(user):
    # seen all notification
    the_filter = Q(Q(thread__second=user) & ~Q(thread__first=user) & Q(seen=False))
    ChatMessage.objects.filter(the_filter).update(seen=True)
    # find last chat
    thread = Thread.objects.filter(Q(first=user) | Q(second=user)).last()
    if not thread:
        completed_app = Appointment.objects.filter(Q(status="COMPLETED") & Q(patient__user=user)).last()
        if not completed_app:
            # print("you dont have any chat options")
            return HttpResponseNotFound()
        thread = Thread.objects.create(first=user, second=completed_app.doctor.user)

    if thread.first == user:
        return f"/chat/{thread.second.phone}/"
    else:
        return f"/chat/{thread.first.phone}/"


@register.simple_tag
def feedback_your_doctor(user_id, doctor_id):
    completed_appointment = Appointment.objects.filter(
        patient__user__id=user_id, doctor__user__id=doctor_id, status="COMPLETED", feedback_status=False
    )
    if not completed_appointment:
        return HttpResponseNotFound()
    return f"/patient/review/{completed_appointment[0].id}/"


@register.simple_tag
def total_notifications(patient__user):
    notifications = Notification.objects.filter(receiver=patient__user, seen=False).count()
    return notifications


@register.simple_tag
def total_chat_notifications(patient__user):
    # check if there is any unseen chat and count it 
    the_filter = Q(Q(thread__second=patient__user) & ~Q(thread__first=patient__user) & Q(seen=False))
    chat_queryset = ChatMessage.objects.filter(the_filter).distinct().count()
    return chat_queryset

@register.simple_tag
def is_file(file_url):
    the_bool = 'Image'
    print('value fo file_url')
    print(file_url)
    extension = str(file_url).split('.')[-1]
    print('value of extension ============-------===========')
    print(extension)
    if extension == 'pdf':
        the_bool = 'Attachment'
    return the_bool

