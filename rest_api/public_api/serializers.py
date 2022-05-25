from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.models import RelativeRelation, BloodGroup, Doctor, Service, Speciality, DoctorTitle, SpecialityCategory
from blog.models import Post
from home.models import City, District

User = get_user_model()

def dynamic_fields(self, args, kwargs):
    fields = kwargs.pop("fields", None)
    exclude = kwargs.pop("exclude", None)
    super(self.__class__, self).__init__(*args, **kwargs)
    # setting fields dynamically
    fields and [self.fields.pop(field_name) for field_name in set(self.fields) - set(fields)]
    exclude and [self.fields.pop(field_name) for field_name in set(self.fields) if field_name in set(exclude)]


class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        return dynamic_fields(self, args, kwargs)

    class Meta:
        model = User
        fields = "__all__"

class DoctorSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(fields=("full_name", "rtl_full_name", "avatar"), source="user")
    title = serializers.CharField()

    class Meta:
        model = Doctor
        fields = (
            "pk",
            "title",
            "doctor",
            "fee",
            "bio",
            # "doc_license_no",
            # "farsi_bio",
            # "pashto_bio",
        )


class DoctorPublicProfileSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(fields=("full_name", "rtl_full_name", "date_of_birth", "gender", "avatar"), source="user")
    title = serializers.CharField()

    class Meta:
        model = Doctor
        fields = (
            "title",
            "doctor",
            "fee",
            "bio",
            "doc_license_no",
            "farsi_bio",
            "pashto_bio",
            "service",
            "condition",
            "speciality",
        )


class RelativeRelationshipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelativeRelation
        fields = "__all__"


class BloodGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodGroup
        fields = "__all__"


class PostListSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="get_language_display")
    blogger = UserSerializer(fields=("full_name", "rtl_full_name", "avatar"), source="blogger.user")

    class Meta:
        model = Post
        fields = "id", "title", "language", "blogger"

    def to_representation(self, instance):
        data = super(self.__class__, self).to_representation(instance)
        data["category"] = instance.category.all().values("name")
        return data


class PostSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="get_language_display")
    blogger = UserSerializer(fields=("full_name", "rtl_full_name", "avatar"), source="blogger.user")

    class Meta:
        model = Post
        fields = "id", "language", "blogger", "title", "body", "view", "active"

    def to_representation(self, instance):
        data = super(self.__class__, self).to_representation(instance)
        data["category"] = instance.category.all().values("name", "farsi_name", "pashto_name")
        return data


class DoctorTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorTitle
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"

