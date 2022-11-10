from django.contrib import admin

from .models import BlogComment, BlogPost, Page, TodoItem

admin.site.register(BlogComment)
admin.site.register(BlogPost)
admin.site.register(Page)
admin.site.register(TodoItem)
