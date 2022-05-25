
from appointment.models import Appointment
from chat.views import post_response
from chat.models import ChatMessage, Thread
from rest_framework import mixins, serializers, views
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.mixins import *
from rest_framework import permissions
from datetime import date
from notification import notification_manager as notification_manager
from rest_api.user_api.permissins import IsOwnerOrReadOnlyDoctor, IsOwnerOrReadOnly
from django.contrib.auth import get_user_model

from django.db.models import Q, F

from rest_api.utils.pagination import CustomPagination
# from django.core import serializers as core_serializer
from .serializers import (
     ChatSerializer, MultipleAttachmentSerializer, 
     MultipleImageSerializer, ChatUserSerializer)

User = get_user_model()


class ChatUser(generics.ListAPIView):
     permission_classes = [permissions.IsAuthenticated]
     serializer_class = ChatUserSerializer
     pagination_class = CustomPagination
     
     def get_queryset(self):
          print('inside the get_queryset00000------')
          query = self.request.GET.get('q')
          print('value of query')
          print(query)
          try:
               me = self.request.user
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
               user_list = User.objects.filter(the_filter).exclude(id=me.id)
               # use annotate or segregation to order the user chat by last having conversation
          except:
               user_list = User.objects.none()
          return user_list


class ChattAPIView(mixins.CreateModelMixin, generics.ListAPIView):
     permission_classes       = [permissions.IsAuthenticated]
     serializer_class         = ChatSerializer
     pagination_class  = CustomPagination

     def get_queryset(self):
          try:
               me = self.request.user
               the_phone = self.kwargs['username']
               if the_phone == me.phone:
                    chat_messages = ChatMessage.object.none()
               else:
                    other_user = generics.get_object_or_404(User, phone=the_phone)
                    thread = Thread.objects.get_or_new(me, other_user)[0]
                    chat_messages = ChatMessage.objects.filter(thread=thread.id).order_by('-timestamp')
          except:
               chat_messages = ChatMessage.objects.none()
          return chat_messages

     def post(self, request, *args, **kwargs):
          raw_data = request.data
          print('value of raw_data')
          print(raw_data)
          user = self.request.user
          the_phone = self.kwargs['username']
          other_user = generics.get_object_or_404(User, phone=the_phone)
          thread = Thread.objects.get_or_new(user, other_user)[0]
          the_response = post_response(raw_data, thread, user)
          print('value of the_response')
          print(the_response)
          return Response(the_response)