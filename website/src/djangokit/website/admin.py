from django.contrib import admin

from .models import BlogPost, Page, TodoItem

admin.site.register(BlogPost)
admin.site.register(Page)
admin.site.register(TodoItem)
