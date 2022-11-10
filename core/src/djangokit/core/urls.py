from django.contrib import admin
from django.urls import include, path

from .routes import discover_routes
from .views import error, user

urlpatterns = [
    path("$admin/", admin.site.urls),
    path("$api/current-user", user.get_current_user),
    path("", include(discover_routes())),
]


handler400 = error.bad_request
handler403 = error.permission_denied
handler404 = error.page_not_found
handler500 = error.server_error
