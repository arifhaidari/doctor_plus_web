from django import template
from ..models import Post, PostCategory


register = template.Library()


@register.simple_tag
def recent_posts():
    return "yes"


@register.inclusion_tag("blog/templatetag_files/recent_posts.html")
def show_latest_posts(count=5):
    latest_posts = Post.objects.all().order_by("-id")[:count]
    return {"recent_posts": latest_posts}


@register.inclusion_tag("blog/templatetag_files/blog_categories.html")
def show_categories():
    return {"categories": PostCategory.objects.all()}


@register.simple_tag
def split_by_words(text, count=35):
    return " ".join(text.split()[:count])
