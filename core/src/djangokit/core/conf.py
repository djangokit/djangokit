import dataclasses
import json
import os
from functools import cached_property
from typing import Any, Dict, List, Optional

import dotenv
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from .checks import make_error

NOT_SET = object()


@dataclasses.dataclass
class Settings:
    """DjangoKit settings.

    This defines the available DjangoKit settings, their types, and
    their default values.

    When a setting is accessed, its value will be retrieved from the
    `DJANGOKIT` dict in the project's Django settings module,if present,
    or the default value defined in `known_settings` will be used.

    .. note::
        Settings are cached the first time they're accessed and can be
        cleared using `settings.clear()` or individually using
        `del settings.<name>`. Clearing is only necessary if the
        `DJANGOKIT` settings are dynamically updated after Django
        startup (e.g., in tests).

    """

    known_settings = {
        "package": {
            "type": str,
        },
        "global_css": {
            "type": list,
            "default": ["global.css"],
        },
    }

    @cached_property
    def package(self) -> str:
        """The project's top level package name."""
        return self._get_required("package")

    @cached_property
    def global_css(self) -> List[str]:
        """CSS files to link in app.html template."""
        return self._get_optional("global_css")

    def as_dict(self):
        """Return a dict with *all* DjangoKit settings.

        This will include defaults plus any values set in the project's
        Django settings module in the `DJANGOKIT` dict.

        """
        return {name: getattr(self, name) for name in self.known_settings}

    def clear(self):
        """Clear all cached DjangoKit settings."""
        for name in self.known_settings:
            if hasattr(self, name):
                delattr(self, name)

    @property
    def _dk_settings(self):
        """Retrieve `DJANGOKIT` dict from Django settings module."""
        try:
            return django_settings.DJANGOKIT
        except AttributeError:
            err = make_error("E000")
            raise ImproperlyConfigured(err.msg)

    def _get_required(self, name):
        if name in self._dk_settings:
            value = self._dk_settings[name]
            self._check_type(name, value)
            return value
        err = make_error("E001", name)
        raise ImproperlyConfigured(err.msg)

    def _get_optional(self, name):
        if name in self._dk_settings:
            value = self._dk_settings[name]
            self._check_type(name, value)
        else:
            value = self.known_settings[name]
        return value

    def _check_type(self, name, value):
        type_ = self.known_settings[name]["type"]
        if not isinstance(value, type_):
            err = make_error("E002", name=name, type=type_, value=value)
            raise ImproperlyConfigured(err.msg)


settings = Settings()


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
