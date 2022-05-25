from django.db import models
from django.conf import settings
from django.db.models import Q
from .validators import image_valid_size, image_valid_type
from .validators import attachment_valid_size, attachment_valid_type


class ThreadManager(models.Manager):
    class Meta:
        app_label = "chat"

    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_username):  # get_or_create
        username = user.phone
        other_username = other_username.phone
        if username == other_username:
            return None
        qlookup1 = Q(first__phone=username) & Q(second__phone=other_username)
        qlookup2 = Q(first__phone=other_username) & Q(second__phone=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by("timestamp").first(), False
        else:
            Klass = user.__class__
            user2 = Klass.objects.get(phone=other_username)
            if user != user2:
                obj = self.model(first=user, second=user2)
                obj.save()
                return obj, True
            return None, False


class Thread(models.Model):
    first = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_thread_first")
    second = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_thread_second")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    def __str__(self):
        return f"{self.first} - {self.second}"

    @property
    def room_group_name(self):
        return f"chat_{self.id}"

    # def broadcast(self, msg=None):
    #     if msg is not None:
    #         broadcast_msg_to_chat(msg, group_name=self.room_group_name, user="admin")
    #         return True
    #     return False


def upload_img_dir(instance, filename):
    return f"chat/images/user_{instance.message.user.id}/{filename}"


def upload_att_dir(instance, filename):
    return f"chat/attachment/user_{instance.message.user.id}/{filename}"


def upload_voice_dir(instance, filename):
    return f"chat/voice/user_{instance.user.id}/{filename}"


class ChatMessage(models.Model):
    thread = models.ForeignKey("Thread", null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", verbose_name="sender", on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    voice = models.FileField(upload_to=upload_voice_dir, blank=True, null=True)
    seen = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.user} - {self.message}"


class MultipleImage(models.Model):
    message = models.ForeignKey("ChatMessage", on_delete=models.CASCADE, verbose_name="Message")
    image = models.ImageField(
        upload_to=upload_img_dir, blank=True, null=True, validators=[image_valid_size, image_valid_type]
    )

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return str(self.image)


class MultipleAttchment(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, verbose_name="Message", related_name='multipleattach')
    attachment = models.FileField(
        upload_to=upload_att_dir, blank=True, null=True, validators=[attachment_valid_size, attachment_valid_type]
    )

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return str(self.attachment)
