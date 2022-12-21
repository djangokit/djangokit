from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .routes import discover_routes
from .views import error, user

dk_settings = settings.DJANGOKIT
prefix = dk_settings.prefix
admin_prefix = dk_settings.admin_prefix
current_user_path = dk_settings.current_user_path

urlpatterns = [
    # Django Admin
    path(f"{prefix}{admin_prefix}", admin.site.urls),
    # Current user
    path(f"{prefix}{current_user_path}", user.get_current_user),
    # Routes
    path(prefix, include(discover_routes())),
]


handler400 = error.bad_request
handler403 = error.permission_denied
handler404 = error.page_not_found
handler500 = error.server_error
