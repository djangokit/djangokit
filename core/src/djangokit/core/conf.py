"""DjangoKit settings.

DjangoKit settings are set in the `DJANGOKIT` dict in a project's Django
settings module::

    DJANGOKIT = {"package": "my_app"}

When accessing a project's DjangoKit settings, it's generally preferable
to use the `settings` object exported from this module rather than
accessing the `DJANGOKIT` dict directly::

    from djangokit.core.conf import settings

    settings.package # -> django.conf.settings.DJANGOKIT["package"]

When accessing an optional DjangoKit setting, the default value will
automatically be used if it's not set in the `DJANGOKIT` dict::

    settings.global_css  # -> ["global.css"]

"""
import dataclasses
import json
import os
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import dotenv
from django.apps import apps
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

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
        Settings are cached the first time they're accessed. Individual
        settings can be cleared using `del settings.<name>`. Clearing is
        only necessary if the `DJANGOKIT` settings are dynamically
        updated after Django startup (e.g., in tests).

    """

    known_settings = {
        "package": {
            "type": str,
        },
        "app_label": {
            "type": str,
            "default_factory": lambda s: s.package.replace(".", "_"),
        },
        "global_css": {
            "type": list,
            "default": ["global.css"],
        },
        "serialize_current_user": {
            "type": str,
            "default": "djangokit.core.user.serialize_current_user",
        },
    }

    @cached_property
    def package(self) -> str:
        """The project's top level package name."""
        return self._get_required("package")

    @cached_property
    def app_label(self) -> str:
        """The project's Django app label.

        Defaults to package name with dots replaced with underscores.

        .. note::
            In most cases, this shouldn't need to be set explicitly.
            It's only needed if the project's app label differs from
            its top level package name.

        """
        return self._get_optional("app_label")

    @cached_property
    def global_css(self) -> List[str]:
        """CSS files to link in app.html template."""
        return self._get_optional("global_css")

    @cached_property
    def app_dir(self) -> Path:
        app = apps.get_app_config(self.app_label)
        return Path(app.path)

    @cached_property
    def models_dir(self) -> Path:
        return self.app_dir / "models"

    @cached_property
    def routes_dir(self) -> Path:
        return self.app_dir / "routes"

    @cached_property
    def routes_package(self) -> Path:
        return f"{self.package}.routes"

    @cached_property
    def static_build_dir(self) -> Path:
        return self.app_dir / "static" / "build"

    @cached_property
    def serialize_current_user(self) -> Callable[[Any], Dict[str, Any]]:
        serializer = self._get_optional("serialize_current_user")
        if isinstance(serializer, str):
            serializer = import_string(serializer)
        return serializer

    def as_dict(self):
        """Return a dict with *all* DjangoKit settings.

        This will include defaults plus any values set in the project's
        Django settings module in the `DJANGOKIT` dict.

        """
        return {name: getattr(self, name) for name in self.known_settings}

    @property
    def _settings(self):
        """Retrieve `DJANGOKIT` dict from Django settings module."""
        try:
            return django_settings.DJANGOKIT
        except AttributeError:
            err = make_error("E000")
            raise ImproperlyConfigured(err.msg)

    def _get_required(self, name):
        if name in self._settings:
            value = self._settings[name]
            self._check_type(name, value)
            return value
        err = make_error("E001", name)
        raise ImproperlyConfigured(err.msg)

    def _get_optional(self, name):
        if name in self._settings:
            value = self._settings[name]
            self._check_type(name, value)
        else:
            info = self.known_settings[name]
            if "default" in info:
                value = info["default"]
            elif "default_factory" in info:
                value = info["default_factory"](self)
            else:
                raise ImproperlyConfigured(
                    "Optional setting must specify a default value or "
                    "a default factory."
                )
        return value

    def _check_type(self, name, value):
        type_ = self.known_settings[name]["type"]
        if not isinstance(value, type_):
            err = make_error("E002", name=name, type=type_, value=value)
            raise ImproperlyConfigured(err.msg)

    def __getattr__(self, name):
        """Proxy Django settings."""
        return getattr(django_settings, name)


settings = Settings()


def load_dotenv(path=".env") -> bool:
    """Load settings from .env file into environ."""
    return dotenv.load_dotenv(path)


def dotenv_settings(path=".env") -> Dict[str, Optional[str]]:
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
