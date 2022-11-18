import dataclasses
from typing import Any, Dict, Optional

from django.conf import settings
from django.core.checks import Error

MESSAGES = {
    "E000": (
        "The DJANGOKIT setting must be present in your project's "
        "Django settings module."
    ),
    "E001": (
        "DjangoKit setting {name} must be set in your project's Django "
        "settings module as a key of the DJANGOKIT setting."
    ),
    "E002": (
        "DjangoKit setting {name} has incorrect type. Expected "
        "{type.__name__}; got {value.__class__.__name__}."
    ),
    "E003": "Unknown DjangoKit setting: {name}.",
}


def make_error(
    code: str,
    field: Optional[dataclasses.Field],
    **data: Dict[str, Any],
) -> Error:
    message = MESSAGES[code]
    if field is None:
        message = message.format(**data)
    else:
        message = message.format(name=field.name, type=field.type, **data)
    return Error(message, id=f"djangokit.{code}")


def check_settings(**kwargs):
    # 1. Check for required settings
    # 2. Ensure settings are of correct type
    # 3. Check for unknown settings
    from .conf import Settings  # noqa: avoid circular import

    errors = []

    if not hasattr(settings, "DJANGOKIT"):
        errors.append(make_error("E000", None))
        return errors

    dk_settings = settings.DJANGOKIT
    fields = dataclasses.fields(Settings)
    fields: Dict[str, dataclasses.Field] = {field.name: field for field in fields}

    for name, field in fields.items():
        if name in dk_settings:
            value = dk_settings[name]
            if not isinstance(value, field.type):
                errors.append(make_error("E002", field, value=value))
        elif field.default is dataclasses.MISSING:
            errors.append(make_error("E001", field))

    for name in dk_settings:
        if name not in fields:
            errors.append(make_error("E003", field))

    return errors


CHECKS = [
    obj
    for name, obj in globals().items()
    if callable(obj) and name.startswith("check_")
]
