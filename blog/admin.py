from django.contrib import admin

from .models import PostCategory, Post, PostImages


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "farsi_name", "pashto_name")


class InlinePostImages(admin.TabularInline):
    model = PostImages
    extra = 0


# class InlinePostTags(admin.TabularInline):
#     model = PostTag
#     extra = 0


class PostAdmin(admin.ModelAdmin):
    inlines = [InlinePostImages]
    list_display = ("id", "title", "blogger", "timestamp", "active")
    search_fields = ("title",)
    ordering = ("title", "active")
    list_filter = ("active", "category")


admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(Post, PostAdmin)
