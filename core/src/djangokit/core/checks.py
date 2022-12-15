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
    "E001": "DjangoKit setting {name} must be set in your project's settings.",
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
    from .conf import KNOWN_SETTINGS  # noqa: avoid circular import

    errors = []

    if not hasattr(settings, "DJANGOKIT"):
        errors.append(make_error("E000"))
        return errors

    dk_settings = settings.DJANGOKIT

    for name, info in KNOWN_SETTINGS.items():
        if name in dk_settings:
            type_ = info["type"]
            value = dk_settings[name]
            if not isinstance(value, type_):
                errors.append(make_error("E002", name=name, type=type_, value=value))
        elif not ("default" in info or "default_factory" in info):
            errors.append(make_error("E001", name=name))

    for name in dk_settings:
        if name not in KNOWN_SETTINGS:
            errors.append(make_error("E003", name=name))

    return errors


CHECKS = [
    obj
    for name, obj in globals().items()
    if callable(obj) and name.startswith("check_")
]
