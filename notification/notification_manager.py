from django.shortcuts import get_object_or_404
from .models import Notification
from user.models import User
# from appointment.models import Feedback, FeedbackReplies

###################### Appt Manager #####################

def appt_canceled_by_doctor(appt_object):
    print('inside the appt_canceled_by_doctor')
    print(appt_object.id)
    try:
        body = f"Your appointment with {appt_object.doctor} on {appt_object.appt_date} at {appt_object.start_appt_time}-{appt_object.end_appt_time} has been canceled by doctor."
        Notification.objects.create(
            title="Appointment Canceled!",
            body=body,
            receiver=appt_object.patient.user,
            appt = appt_object,
            category=Notification.Categories.appt_cancelation
        )
    except Exception as e:
        print('valeu fo errororororo0000')
        print(e)


def appt_cancel_by_patient(appt_object):
    try:
        patient = appt_object.patient
        if appt_object.relative is not None:
            patient = appt_object.relative
        body = f"Your appointment with {appt_object.patient} on {appt_object.appt_date} at {appt_object.start_appt_time}-{appt_object.end_appt_time} has been canceled by patient."
        Notification.objects.create(
            title="Appointment Canceled!",
            body=body,
            receiver=appt_object.doctor.user,
            appt = appt_object,
            category=Notification.Categories.appt_cancelation
        )
    except:
        pass



##################### Review Manager #####################

def review_requested_from_patient(appt_object):
    try:
        body = f"Please place your feedback and a review for your last appointment with doctor {appt_object} on {appt_object.appt_date} at {appt_object.start_appt_time}-{appt_object.end_appt_time}."
        Notification.objects.create(
            title="Leave A Feedback & Review",
            body=body,
            receiver=appt_object.patient.user,
            appt = appt_object,
            category=Notification.Categories.review
        )
    except:
        pass

def review_created_by_patient(appt_object, comment):
    try:
        patient = appt_object.patient
        if appt_object.relative is not None:
            patient = appt_object.relative
        pronoun = 'his' if patient.user.gender == 'Male' else 'her'
        and_review = ' and review' if (comment != '' or comment is not None) else ''
        body = f"{patient} left feedback{and_review} for {pronoun} last appointment with you on {appt_object.appt_date} at {appt_object.start_appt_time}-{appt_object.end_appt_time}"
        Notification.objects.create(
            title=f"You have recieved a feedback{and_review}",
            body=body,
            receiver=appt_object.doctor.user,
            appt = appt_object,
            category=Notification.Categories.review
        )
        appt_object.feedback_status = True
        appt_object.save()
        print('finally got here ++++++++++')
    except Exception as e:
        print('value of eroror in the crating the ntofiaitn ')
        print(e)



def review_relplied_by_doctor(appt_object, reply):
    try:
        Notification.objects.create(
            title=f"{appt_object.doctor} Replied To Your Review On {appt_object.appt_date} Appointment At {appt_object.start_appt_time}-{appt_object.end_appt_time}",
            body=reply,
            receiver=appt_object.patient.user,
            appt = appt_object,
            category=Notification.Categories.review_reply
        )
    except Exception as e:
        print('value fo eroror in notification manager')
        print(e)


