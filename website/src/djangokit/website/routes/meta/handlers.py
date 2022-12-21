import os

from django.conf import settings

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
        "env": settings.ENV,
        "version": os.getenv("VERSION"),
    }

    if request.user.is_superuser:
        dk_settings = settings.DJANGOKIT.as_dict()
        for n, v in dk_settings.items():
            if callable(v):
                dk_settings[n] = f"{v.__module__}.{v.__name__}"
        data["settings"] = {n: getattr(settings, n) for n in INCLUDE_SETTINGS}
        data["settings"]["DJANGOKIT"] = dk_settings

    return data
