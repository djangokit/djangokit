import dataclasses
from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

NOT_SET = object()


@dataclasses.dataclass
class Settings:
    package: str
    """The project's top level package name."""


@lru_cache
def get_setting(name: str, default=NOT_SET):
    """Get a DjangoKit setting from Django settings.

    DjangoKit settings are defined as keys of the top level `DJANGOKIT`
    setting in a project's Django settings module::

        # <package>/settings.py
        DJANGOKIT = {
            "package": "my_package",
        }

    For optional settings that haven't been set in the Django settings
    module, a default value may be passed; otherwise, the default value
    specified in `data`:Defaults` will be used.

    """
    dk_settings = settings.DJANGOKIT
    fields = dataclasses.fields(Settings)
    fields = {field.name: field for field in fields}

    if name not in fields:
        raise LookupError(f"Unknown DjangoKit setting: {name}")

    if name in dk_settings:
        return dk_settings[name]

    if default is NOT_SET:
        field = fields[name]
        default = field.default

        # NOTE: This is only needed because the project's urls.py calls
        #       create_routes(), which in turn calls this function
        #       BEFORE the checks in apps.py are run.
        if default is dataclasses.MISSING:
            raise ImproperlyConfigured(f"DjangoKit setting is required: {name}")

    return default
