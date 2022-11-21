from typing import Any, Dict

from django.conf import settings
from django.core.checks import Error

MESSAGES = {
    # Vars:
    "E000": (
        "The DJANGOKIT setting must be present in your project's "
        "Django settings module."
    ),
    # Vars: name
    "E001": (
        "DjangoKit setting {name} must be set in your project's Django "
        "settings module as a key of the DJANGOKIT setting."
    ),
    # Vars: name, type, value
    "E002": (
        "DjangoKit setting {name} has incorrect type. Expected "
        "{type.__name__}; got {value.__class__.__name__}."
    ),
    # Vars: name
    "E003": "Unknown DjangoKit setting: {name}.",
}


def make_error(code: str, **data: Dict[str, Any]) -> Error:
    message = MESSAGES[code]
    message = message.format(**data)
    return Error(message, id=f"djangokit.{code}")


def check_settings(**kwargs):
    # 1. Check for required settings
    # 2. Ensure settings are of correct type
    # 3. Check for unknown settings
    from .conf import Settings  # noqa: avoid circular import

    errors = []

    if not hasattr(settings, "DJANGOKIT"):
        errors.append(make_error("E000"))
        return errors

    dk_settings = settings.DJANGOKIT
    known_settings = Settings.known_settings

    for name, info in known_settings.items():
        if name in dk_settings:
            type_ = info["type"]
            value = dk_settings[name]
            if not isinstance(value, type_):
                errors.append(make_error("E002", name=name, type=type_, value=value))
        elif "default" not in info:
            errors.append(make_error("E001", name=name))

    for name in dk_settings:
        if name not in known_settings:
            errors.append(make_error("E003", name=name))

    return errors


CHECKS = [
    obj
    for name, obj in globals().items()
    if callable(obj) and name.startswith("check_")
]
