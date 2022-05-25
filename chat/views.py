# from msilib.schema import ListView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.http import JsonResponse

from appointment.models import Appointment
from rest_api.chat_api.serializers import ChatUserSerializer
from .models import MultipleAttchment, MultipleImage, Thread, ChatMessage
from .validators import uploaded_attachments_validation, uploaded_images_validation

# from notification import chat_notifications as notification_manager
from django.db.models import OuterRef, Subquery

User = get_user_model()

def chatview(request, username, *args, **kwargs):
     try:
          me = request.user
          print('avlue of username ===----')
          print(username)
          if username == me.phone:
               # this is a validation to should not allow others to enter this conversation except me 
               return HttpResponseNotFound()
          
          if str(username) == '351':
               return HttpResponseNotFound()
          other_user = get_object_or_404(User, phone=username)
          user_list_raw = chat_user_list('', me, other_user=other_user)
          user_list = ChatUserSerializer(user_list_raw, context = {'request': request}, many=True).data
          thread = Thread.objects.get_or_new(me, other_user)[0]
          chatMessages = list(ChatMessage.objects.filter(thread=thread.id))

          if request.method == "POST":
               print('the request is post----------')
               the_response = post_response(request.FILES, thread, me)
               return JsonResponse(the_response)

          context = {
               "other_user": other_user,
               "chatmessages": chatMessages,
               "user_list": user_list,
          }
     except:
          context = {
               "other_user": None,
               "chatmessages": None,
               "user_list": None,
          }
     return render(request, 'chat/chat_template.html', context)


def post_response(raw_data, thread, me):
     if raw_data.get("file"):
          e_message = ChatMessage.objects.create(thread=thread, user=me, message="")
          valid_attachments = uploaded_attachments_validation(raw_data.getlist("file"))
          for x in valid_attachments:
               MultipleAttchment(message=e_message, attachment=x).save()
          response = {
               "status": "success",
               "attachmentNames": [x.attachment.url for x in MultipleAttchment.objects.filter(message=e_message)],
          }
          return response

     if raw_data.get("image"):
          e_message = ChatMessage.objects.create(thread=thread, user=me, message="")
          valid_images = uploaded_images_validation(raw_data.getlist("image"))
          for x in valid_images:
               MultipleImage(message=e_message, image=x).save()

          return {"status": "success", "imageNames": [x.image.url for x in MultipleImage.objects.filter(message=e_message)]}
          
     if raw_data.get("audio"):
          e_message = ChatMessage.objects.create(thread=thread, user=me, message="", voice=raw_data.get("audio"))
          return {"status": "success", "voice": ChatMessage.objects.last().voice.url}

# class ChatUserList(ListView):
     
def chat_user_list(query, me, other_user = None):
     try:
          chat_thread_list = Thread.objects.filter(Q(first=me) | Q(second=me)).distinct().values_list(F('id'), flat=True)
          thread_id_list = list(chat_thread_list)
          chat_list = ChatMessage.objects.filter(thread_id__in=thread_id_list).distinct().values_list(F('user__id'), flat=True)
          chat_user_id_list = list(chat_list)
          is_doctor = False
          try:
               if me.doctor:
                    is_doctor = True
          except:
               is_doctor = False
          if not is_doctor:
               print('the user a patient bro')
               doctor_list = me.patient.appointment_set.filter(status=Appointment.ApptStatus.COMPLETED).distinct().values_list(F('doctor__user'), flat=True)
               doctor_id_list = list(doctor_list)
               chat_user_id_list = chat_user_id_list + doctor_id_list
               # get all doctor which you have completed appt with and add this list at the end of the list 
               # first check if the list is less than 20 items then add another 20 and then add more 
               # check if the remaining list is more than 20 then cut 20 from the main list and add more 
               # 351_tackle solved just check
          if is_doctor:
               # maybe we dont need the rest we only need this part to get our patient who completed or booked appt
               # but we have to find a mechanism to order them by last sent text
               patient_list = me.doctor.appointment_set.filter(Q(relative=None) & Q(status=Appointment.ApptStatus.COMPLETED)).values_list(F('patient__user'), flat=True)
               patient_id_list = list(patient_list)
               chat_user_id_list = list(set(chat_user_id_list + patient_id_list))
          the_filter = Q(id__in=chat_user_id_list)
          if query is not None and query != '':
               the_filter.add(Q(Q(full_name__icontains=query) | Q(rtl_full_name__contains=query)), Q.AND)
          if other_user is not None:
               the_filter.add(~Q(id=other_user.id), Q.AND)
          user_list = User.objects.filter(the_filter).exclude(id=me.id)
          # if other_user is not None:
          #      print('other_user is here bro---=====')
          #      print(other_user.id)
          #      print(me.id)
          #      user_list.exclude(id=other_user.id)
          # use annotate or segregation to order the user chat by last having conversation
     except:
          user_list = User.objects.none()
     return user_list