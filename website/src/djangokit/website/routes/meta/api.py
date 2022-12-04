from os import getenv

from django.conf import settings as django_settings
from djangokit.core.conf import settings


INCLUDE_SETTINGS = (
    "DEBUG",
    "ALLOWED_HOSTS",
    "ROOT_URLCONF",
    "WSGI_APPLICATION",
    "TIME_ZONE",
    "LOGIN_URL",
    "STATIC_ROOT",
    "STATIC_URL",
    "STATICFILES_STORAGE",
)


def get(request):
    data = {
        "env": getenv("ENV", "development"),
        "version": getenv("VERSION"),
    }

    if request.user.is_superuser:
        dk_settings = settings.as_dict()
        for n, v in dk_settings.items():
            if callable(v):
                dk_settings[n] = f"{v.__module__}.{v.__name__}"
        data["settings"] = {n: getattr(django_settings, n) for n in INCLUDE_SETTINGS}
        data["settings"]["DJANGOKIT"] = dk_settings

    return data
