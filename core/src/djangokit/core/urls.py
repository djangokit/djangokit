from django.contrib import admin
from django.urls import include, path

from .routes import discover_routes
from .views import error

urlpatterns = [
    path("", include(discover_routes())),
    path("$admin/", admin.site.urls),
]


handler400 = error.bad_request
handler403 = error.permission_denied
handler404 = error.page_not_found
handler500 = error.server_error
