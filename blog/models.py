from django.db import models


class Post(models.Model):
    Languages = (0, "English"), (1, "دری"), (2, "پشتو")
    blogger = models.ForeignKey("user.Blogger", on_delete=models.SET_NULL, null=True, blank=True)
    language = models.SmallIntegerField(choices=Languages, default=0)
    title = models.CharField(max_length=256)
    body = models.TextField()
    category = models.ManyToManyField("PostCategory", blank=True)
    view = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or ""


def upload_post_img(instance, filename):
    return f"posts/user_{instance.post.blogger.user.id}/{filename}/"


class PostImages(models.Model):
    image = models.ImageField(upload_to=upload_post_img)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="images")

    def __str__(self):
        return str(self.image)


class PostCategory(models.Model):
    name = models.CharField(max_length=256)
    farsi_name = models.CharField(max_length=256)
    pashto_name = models.CharField(max_length=256)

    def __str__(self):
        return self.name or self.farsi_name or self.pashto_name or ""
