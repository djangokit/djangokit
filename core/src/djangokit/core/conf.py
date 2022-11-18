import dataclasses
import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional

import dotenv
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .checks import make_error

NOT_SET = object()


@dataclasses.dataclass
class Settings:
    """DjangoKit settings.

    This defines the available DjangoKit settings, their types, and
    their default values.

    """

    package: str
    """The project's top level package name."""

    global_css: list = ("global.css",)
    """CSS files to link in app.html template."""


@lru_cache
def get_setting(name: str, default=NOT_SET):
    """Get a DjangoKit setting from the project's Django settings.

    DjangoKit settings are defined as keys of the top level `DJANGOKIT`
    setting in a project's Django settings module::

        # <package>/settings.py
        DJANGOKIT = {
            "package": "my_package",
            "global.css": ["tailwind.css"],
        }

    For optional settings that haven't been set in the Django settings
    module, a default value may be passed; otherwise, the default value
    specified in `data`:Defaults` will be used.

    """
    if not hasattr(settings, "DJANGOKIT"):
        err = make_error("E000", None)
        raise ImproperlyConfigured(err.msg)

    dk_settings = settings.DJANGOKIT
    fields = dataclasses.fields(Settings)
    fields = {field.name: field for field in fields}

    if name not in fields:
        err = make_error("E003", None, name=name)
        raise LookupError(err.msg)

    field = fields[name]

    # NOTE: Even though there are startup checks to ensure required DK
    #       settings are present and that DK settings have the correct
    #       type, the checks here are needed in case DK settings are
    #       accessed early in the Django startup process (as they are
    #       when create_routes() is called from a project's urls.py).
    if name in dk_settings:
        value = dk_settings[name]
        if not isinstance(value, field.type):
            err = make_error("E002", field, value=value)
            raise ImproperlyConfigured(err.msg)
        return value
    elif field.default is dataclasses.MISSING:
        err = make_error("E001", field)
        raise ImproperlyConfigured(err.msg)

    if default is NOT_SET:
        default = field.default

    return default


def load_dotenv(path=".env") -> bool:
    """Load settings from .env file into environ."""
    return dotenv.load_dotenv(path)


def dotenv_values(path=".env") -> Dict[str, Optional[str]]:
    """Load settings from .env file into environ."""
    values = dotenv.dotenv_values(path)
    processed_values = {}
    for name, value in values.items():
        processed_values[name] = convert_env_val(value)
    return processed_values


def getenv(name: str, default: Any = NOT_SET) -> Any:
    """Get setting from environ."""
    if default is NOT_SET:
        value = os.environ[name]
    elif name in os.environ:
        value = os.environ[name]
        value = convert_env_val(value)
    else:
        value = default
    return value


def convert_env_val(value: str) -> Any:
    try:
        value = json.loads(value)
    except ValueError:
        pass
    return value
