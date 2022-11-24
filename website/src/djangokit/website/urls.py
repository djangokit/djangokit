from django.contrib import admin
from django.urls import include, path
from djangokit.core import get_route_urls

urlpatterns = [
    path("", include(get_route_urls())),
    path("$admin/", admin.site.urls),
]
