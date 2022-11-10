from django.contrib import admin
from django.urls import include, path
from djangokit.core import register_routes

from . import routes

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(register_routes(routes))),
]
