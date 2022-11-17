from django.conf import settings

NOT_SET = object()


DEFAULTS = {
    "package": NOT_SET,
}


def get_setting(name: str, default=None):
    """Get a DjangoKit setting."""
    if name not in DEFAULTS:
        raise KeyError(f"Unknown DjangoKit setting: {name}")
    value = settings.DJANGOKIT.get(name, default)
    if value is NOT_SET:
        raise ValueError(f"DjangoKit setting is not set: {name}")
    return value
