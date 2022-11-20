from django.contrib import admin
from django.urls import path
from djangokit.core import create_routes

urlpatterns = [
    path("django-admin/", admin.site.urls),
    create_routes(),
]
