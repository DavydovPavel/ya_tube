from django.contrib import admin
from .models import Post, Group
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models
from ckeditor.widgets import CKEditorWidget


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = '-пусто-'

admin.site.register(Post, PostAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ("title",)

admin.site.register(Group, GroupAdmin)


class FlatPageCustom(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageCustom)
