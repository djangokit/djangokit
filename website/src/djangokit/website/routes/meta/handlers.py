import os

from django.conf import settings
from django.views.debug import SafeExceptionReporterFilter


def get(request):
    """Get meta info, including environment, version, and settings.

    If the `for-menu` query parameter is present in the request, only
    the environment and version will be included.

    """
    safe_filter = SafeExceptionReporterFilter()

    data = {
        "env": settings.ENV,
        "version": os.getenv("VERSION"),
    }

    if "for-menu" in request.GET:
        return data

    if request.user.is_superuser:
        django_settings = safe_filter.get_safe_settings()
        django_settings.pop("DJANGOKIT", None)

        dk_settings = settings.DJANGOKIT.as_dict()
        for n, v in dk_settings.items():
            if callable(v):
                dk_settings[n] = f"{v.__module__}.{v.__name__}"

        data["settings"] = django_settings
        data["settings"]["DJANGOKIT"] = dk_settings

    return data
