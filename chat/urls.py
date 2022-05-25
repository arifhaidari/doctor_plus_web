from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "chat"
urlpatterns = [
    path("<str:username>/", views.chatview, name="chatView"),
    # path("api/", include("chat.api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
