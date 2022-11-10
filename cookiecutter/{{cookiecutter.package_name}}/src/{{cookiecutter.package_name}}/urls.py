from django.contrib import admin
from django.urls import path

from . import routes

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
    ),
]
