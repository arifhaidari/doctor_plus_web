from django.db import models



# Create your models here.
class Notification(models.Model):
    class Meta:
        verbose_name = "Nofitication"
        verbose_name_plural = "Nofitications"
        
    class Categories(models.TextChoices):
        appt_cancelation = 'appt_cancelation'
        review_reply = 'review_reply'
        review = 'review'
    title = models.CharField(max_length=256, blank=True)
    body = models.TextField(null=True, blank=True)
    receiver = models.ForeignKey("user.User", on_delete=models.CASCADE)
    category = models.CharField(choices=Categories.choices, null=True, blank=True, max_length=25)
    appt = models.ForeignKey("appointment.Appointment" ,on_delete=models.SET_NULL, blank=True, null=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}, {self.timestamp}" or "notification_object"


