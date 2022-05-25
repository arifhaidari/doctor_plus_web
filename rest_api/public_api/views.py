
from rest_framework import generics, mixins, permissions, serializers, status
from rest_framework.response import Response
from  rest_api.user_api.permissins import *
from rest_framework import mixins, viewsets, generics

from django.db.models import Q

from user.models import RelativeRelation, BloodGroup, Doctor, Service, Condition, Speciality, DoctorTitle, SpecialityCategory, User
from doctor.models import Disease, Symptoms
from blog.models import Post, PostImages, PostCategory
from home.models import City, District
from . import serializers as ser

class SearchVieSet(viewsets.ModelViewSet):
    serializer_class = ser.DoctorSerializer
    http_method_names = "get", "head", "options", "trace"
    serializer_classes = {
        "list": ser.DoctorSerializer,
        "retrieve": ser.DoctorPublicProfileSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    def get_queryset(self):
        key = self.request.GET.get("q")
        if not key:
            return Doctor.objects.all()
            return Doctor.objects.none()
        print("the key is : ", key)
        qs = Doctor.objects.filter(
            self.query_by_doctor_details(key) | self.query_by_specialities(key) | self.query_by_conditions(key)
        ).distinct()
        return qs

    def query_by_doctor_details(self, key):
        return (
            Q(user__full_name__icontains=key)
            | Q(user__rtl_full_name__icontains=key)
            | Q(user__phone__icontains=key)
            | Q(user__email__icontains=key)
            | Q(user__id__iexact=key)
        )

    def query_by_specialities(self, key):
        specialities = (
            Speciality.objects.filter(
                Q(name__icontains=key)
                | Q(farsi_name__icontains=key)
                | Q(pashto_name__icontains=key)
                | Q(speciality_category__name__icontains=key)
                | Q(speciality_category__farsi_name__icontains=key)
                | Q(speciality_category__pashto_name__icontains=key)
                | self.query_by_diseases(key)
            )
            .values("id")
            .distinct()
        )
        return Q(speciality__in=specialities)

    def query_by_conditions(self, key):
        conditions = (
            Condition.objects.filter(Q(name__iexact=key) | Q(farsi_name__iexact=key) | Q(pashto_name__iexact=key))
            .values("id")
            .distinct()
        )
        return Q(condition__in=conditions)

    def query_by_services(self, key):
        services = (
            Service.objects.filter(Q(name__iexact=key) | Q(farsi_name__iexact=key) | Q(pashto_name__iexact=key))
            .values("id")
            .distinct()
        )
        return Q(service__in=services)

    def query_by_diseases(self, key):
        diseases = (
            Disease.objects.filter(
                Q(name__iexact=key) | Q(farsi_name__iexact=key) | Q(pashto_name__iexact=key) | self.query_by_symptoms(key)
            )
            .values("id")
            .distinct()
        )
        return Q(disease__in=diseases)

    def query_by_symptoms(self, key):
        symptoms = (
            Symptoms.objects.filter(Q(name__iexact=key) | Q(farsi_name__iexact=key) | Q(pashto_name__iexact=key))
            .values("id")
            .distinct()
        )
        return Q(symptom__in=symptoms)


class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_classes = {
        "list": ser.PostListSerializer,
        "retrieve": ser.PostSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, ser.PostListSerializer)

    def get_queryset(self):
        qs = Post.objects.all()
        key = self.request.GET.get("q")
        if key:
            qs = qs.filter(
                Q(title__icontains=key)
                | self.query_by_post_category(key)
                | Q(blogger__user__full_name__icontains=key)
                | Q(blogger__user__rtl_full_name__icontains=key)
            )
        return qs

    def query_by_post_category(self, key):
        categories = (
            PostCategory.objects.filter(Q(name__iexact=key) | Q(farsi_name__iexact=key) | Q(pashto_name__iexact=key))
            .values("id")
            .distinct()
        )
        return Q(category__in=categories)

class RelativeRelationshipsViewSet(generics.ListAPIView):
    queryset = RelativeRelation.objects.all()
    serializer_class = ser.RelativeRelationshipsSerializer


class BloodGroupViewSet(generics.ListAPIView):
    queryset = BloodGroup.objects.all()
    serializer_class = ser.BloodGroupSerializer


class ListDoctorTitleView(generics.ListAPIView):
    queryset = DoctorTitle.objects.all()
    serializer_class = ser.DoctorTitleSerializer



class ListCityView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = ser.CitySerializer


class ListDistrictView(generics.ListAPIView):
    queryset = District.objects.all()
    serializer_class = ser.DistrictSerializer




