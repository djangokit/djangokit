from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .routes import discover_routes
from .views import error, user

dk_settings = settings.DJANGOKIT

urlpatterns = [
    # Django Admin
    path(dk_settings.admin_prefix, admin.site.urls),
    # Current user API
    path(f"{dk_settings.api_prefix}current-user", user.get_current_user),
    # API & page routes
    path(
        dk_settings.mount_point,
        include(
            discover_routes(
                dk_settings.api_prefix,
                dk_settings.page_prefix,
            )
        ),
    ),
]


handler400 = error.bad_request
handler403 = error.permission_denied
handler404 = error.page_not_found
handler500 = error.server_error
