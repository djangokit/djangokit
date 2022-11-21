from django.contrib import admin
from django.urls import path
from djangokit.core import create_routes

urlpatterns = [
    create_routes(),
    path("$admin/", admin.site.urls),
]
