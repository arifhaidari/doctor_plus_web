"""DoctorPlus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("madmin/", include("adminplus.urls", namespace="adminplus")),
    path("", include("home.urls", namespace="home")),
    path("accounts/", include("allauth.urls")),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("user/", include("user.urls", namespace="user")),
    path("appoint/", include("appointment.urls", namespace="appointment")),
    path("blog/", include("blog.urls", namespace="blog")),
    path("chat/", include("chat.urls", namespace="chat")),
    path("doctor/", include("doctor.urls", namespace="doctor")),
    path("patient/", include("patient.urls", namespace="patient")),
    path("relative/", include("relative.urls", namespace="relative")),
    path("medicalrecord/", include("medicalrecord.urls", namespace="medicalrecord")),
    # api
    path("api/", include("rest_api.urls", namespace="rest_api")),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
