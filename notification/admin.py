from django.contrib import admin
from .models import Notification

# Register your models here.


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = "receiver", "category", "title", "body", "timestamp"
    list_filter = ("category",)
    search_fields = ("title",)
