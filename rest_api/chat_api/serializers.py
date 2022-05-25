
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.query_utils import Q
from notification import models
from rest_api.doctor_api.serializers import UserSerializer
from rest_framework import serializers
from chat.models import ChatMessage, MultipleAttchment, MultipleImage, Thread
from notification.models import Notification
# from notification import review_notifications
from django.contrib.auth import get_user_model

User = get_user_model()


def dynamic_fields(self, args, kwargs):
     fields = kwargs.pop("fields", None)
     exclude = kwargs.pop("exclude", None)
     super(self.__class__, self).__init__(*args, **kwargs)
     # setting fields dynamically
     fields and [self.fields.pop(field_name) for field_name in set(self.fields) - set(fields)]
     exclude and [self.fields.pop(field_name) for field_name in set(self.fields) if field_name in set(exclude)]
 
class MultipleImageSerializer(serializers.ModelSerializer):
     # message = ChatSerializer(read_only=True)
     
     class Meta:
          model = MultipleImage
          fields = ('image',)


class MultipleAttachmentSerializer(serializers.ModelSerializer):
     # message = ChatSerializer(read_only=True)
     
     class Meta:
          model = MultipleAttchment
          fields = ('attachment',)
          # fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
     user = UserSerializer(read_only=True, fields=('phone',))
     image_list = MultipleImageSerializer(read_only=True, many=True, source='multipleimage_set')
     attachment_list = MultipleAttachmentSerializer(read_only=True, many=True, source='multipleattach')
     class Meta:
          model = ChatMessage
          # fields = ('',)
          exclude = ('thread',)


class ChatUserSerializer(serializers.ModelSerializer):
     last_text = serializers.SerializerMethodField(read_only=True)
     def get_last_text(self, other_user):
          me = self.context['request'].user
          print('value of me:', me, ', value of other_user: ', other_user)
          thread_object = Thread.objects.get_or_new(me, other_user)[0]
          is_message = ChatMessage.objects.filter(thread=thread_object).order_by("-timestamp")
          # message = 'no_chat_yet'
          last_message_detail = {
               'sent_by_me': False,
               'message_type': 'text',
               'message_text': 'no_chat_yet',
               'timestamp': '',
               'seen': False,
          }
          if is_message.exists():
               chat_object = is_message.first()
               last_message_detail['timestamp'] = chat_object.timestamp
               last_message_detail['message_text'] = chat_object.message
               last_message_detail['seen'] = chat_object.seen
               if chat_object.user == me:
                    last_message_detail['sent_by_me'] = True
               if chat_object.message == '' or chat_object.message is None:
                    if chat_object.voice == '' or chat_object.voice is None:
                         last_message_detail['message_type'] = 'file_attachment'
                    else:
                         last_message_detail['message_type'] = 'voice'
          return last_message_detail
     class Meta:
          model = User
          fields = ('phone', 'full_name', 'rtl_full_name', 'avatar', 'last_text')
          


