from django.contrib import admin
import nested_admin


from .models import Thread, ChatMessage, MultipleImage, MultipleAttchment


admin.site.register(ChatMessage);

class MultipleImage(nested_admin.NestedTabularInline):
    model = MultipleImage
    extra = 0


class MultipleAttachments(nested_admin.NestedTabularInline):
    model = MultipleAttchment
    extra = 0


class ChatMessage(nested_admin.NestedStackedInline):
    model = ChatMessage
    extra = 0
    inlines = [
        MultipleImage,
        MultipleAttachments,
    ]


@admin.register(Thread)
class ThreadAdmin(nested_admin.NestedModelAdmin):
    inlines = [ChatMessage]
    list_display = ("id", "first", "second", "updated", "timestamp")
    list_filter = ("timestamp",)

    class Meta:
        model = Thread


"""
*** django-nested-admin 3.3.3 ***
app: nested_admin
-------------------------------------
django.contrib.admin    nested_admin
ModelAdmin              NestedModelAdmin
InlineModelAdmin        NestedInlineModelAdmin
StackedInline           NestedStackedInline
TabularInline           NestedTabularInline
"""
