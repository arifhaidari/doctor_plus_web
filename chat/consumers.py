from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
import json
from django.db.models import Q

from chat.views import chat_user_list
from .models import Thread, ChatMessage
from django.contrib.auth import get_user_model
# from notification import chat_notifications as notification_manager
from channels.generic.websocket import AsyncWebsocketConsumer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        me = self.scope["user"]
        other_user = self.scope["url_route"]["kwargs"]["username"]
        thread_obj = await self.get_thread(me, other_user)
        self.thread_obj = thread_obj
        self.room_group_name = f"chat_{thread_obj.id}"
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # if you do not call accept it then it will not accept the coonecction 
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print('value of disconnect')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    # Receive message from WebSocket
    async def receive(self, text_data):
        print('inside the receive')
        loaded_data_json = json.loads(text_data)
        message = loaded_data_json.get('message', None)
        print('value of loaded_data_json')
        print(loaded_data_json)
        user = self.scope["user"]
        if message is not None:
            user = self.scope["user"]
            user_phone = "default"
            if user.is_authenticated:
                user_phone = user.phone
                # save it to db
                if not message == "image-files" and not message == "attachment-files" and not message == "voice-message":
                    await self.create_chat_message(user, message)
                    pass
                    # pass
            # we can save the data right here as well as we do save text data 
            # respone
            myResponse = {"message": message, "user_phone": user_phone, 'type': 'chat_message', 'media_type': 'text'}
            if message == "image-files":
                myResponse = {"message": "", "user_phone": user_phone, "images": loaded_data_json.get("images"), 'type': 'chat_message', 'media_type': 'image'}
            if message == "attachment-files":
                print('the attachment is part -----')
                myResponse = {
                    "message": "",
                    "user_phone": user_phone,
                    "attachments": loaded_data_json.get("files"),
                    "type": "chat_message",
                    'media_type': 'attachement'
                }
            if message == "voice-message":
                myResponse = {"message": "", "user_phone": user_phone, "voice": loaded_data_json.get("voice"), "type": "chat_message", 'media_type': 'voice'}

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            myResponse
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        print('iside the chat_message')
        await self.send(text_data=json.dumps(event))
  
    
    @database_sync_to_async
    def get_thread(self, user, other_username):
        other_user_phone = other_username
        other_user = User.objects.get(phone=other_user_phone)
        return Thread.objects.get_or_new(user, other_user)[0]

    @database_sync_to_async
    def create_chat_message(self, me, msg):
        ChatMessage.objects.create(thread=self.thread_obj, user=me, message=msg)
        # sending the notification
        # notification_manager.create_chatmessage_notification(
        #     self.scope["url_route"]["kwargs"]["username"], self.thread_obj, msg
        # )
        