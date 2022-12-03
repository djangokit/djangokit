"""DjangoKit settings.

DjangoKit settings are set in your project's .env file(s) along with
env-specific Django settings:

    # .env.public - public settings common to all environments
    DJANGOKIT_PACKAGE="my_app"
    DJANGOKIT_GLOBAL_CSS=["styles.css"]

    # .env.development - dev-specific settings
    DJANGO_DEBUG=true
    DJANGO_SECRET_KEY="xxx"

    # .env.production - prod-specific settings
    DJANGO_DEBUG=false
    DJANGO_ALLOWED_HOSTS=["example.com"]
    DJANGO_SECRET_KEY="super secret key that shouldn't be stored in git"
    DJANGO_DATABASES_default__NAME="/path/to/db.prod.sqlite3"

> NOTE: You can use JSON values for the settings in your .env files.

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
import socket
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, Dict, List

from django.apps import apps
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .checks import make_error


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

    # XXX: Keep in sync with `.settings.defaults.DJANGOKIT`.
    known_settings = {
        "title": {
            "type": str,
            "default": "DjangoKit Site",
        },
        "description": {
            "type": str,
            "default": "A website made with DjangoKit",
        },
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
        "current_user_serializer": {
            "type": str,
            "default": "djangokit.core.user.current_user_serializer",
        },
        "ssr": {
            "type": bool,
            "default": True,
        },
        "webmaster": {
            "type": str,
            "default": "",
        },
    }

    @cached_property
    def title(self) -> str:
        """Project title.

        Used as the default HTML page title.

        """
        return self._get_required("title")

    @cached_property
    def description(self) -> str:
        """Project description.

        Used as the default meta description.

        """
        return self._get_required("description")

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
    def current_user_serializer(self) -> Callable[[Any], Dict[str, Any]]:
        serializer = self._get_optional("current_user_serializer")
        if isinstance(serializer, str):
            serializer = import_string(serializer)
        return serializer

    @cached_property
    def ssr(self) -> bool:
        return self._get_optional("ssr")

    @cached_property
    def webmaster(self) -> str:
        webmaster = self._get_optional("webmaster")
        if webmaster:
            return webmaster
        hostname = socket.gethostname()
        return f"webmaster@{hostname}"

    @cached_property
    def static_build_dir(self) -> Path:
        return self.app_dir / "static" / "build"

    # Derived settings -------------------------------------------------
    #
    # These are not directly settable in a project.

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

    # Utilities --------------------------------------------------------

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
        """Proxy Django settings.

        XXX: Is this useful and/or a good idea?

        """
        return getattr(django_settings, name)


settings = Settings()
