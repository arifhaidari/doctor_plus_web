from django import forms
from django.forms import inlineformset_factory
from .models import Post, PostImages
from django.contrib.auth import get_user_model

User = get_user_model()


class UpdateBlogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateBlogForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = "__all__"
        exclude = ("blogger", "view")
        labels = {"language": "Language this post appears for"}
        widgets = {
            "language": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"row": "25", "class": "form-control"}),
        }


ImagesFormSet = inlineformset_factory(
    Post,
    PostImages,
    fields=("image",),
    extra=4,
    max_num=4,
    widgets={"image": forms.FileInput(attrs={"class": "form-control"})},
    labels={"image": ""},
)


class UpdateBloggerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # user_id = kwargs.pop("user_id")
        super(UpdateBloggerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ["full_name", "rtl_full_name", "gender", "phone", "email", "date_of_birth", "avatar"]
        labels = {"rtl_full_name": "Dari/Pashto Name"}
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "rtl_full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.widgets.DateInput(attrs={"type": "date", "class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
        }
