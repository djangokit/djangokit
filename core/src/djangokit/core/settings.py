"""Default Django settings module used by DjangoKit projects.

Settings can be set via environment variables in a project's .env
file(s) and/or using standard OS mechanisms.

.. note::
    ALL Django settings can be set via environment variables.

.. note::
    The values of these environment variables will be parsed as JSON,
    if possible.

For a given Django setting, the env var name is the name of the setting
prefixed with `DJANGO_`. For example, here's how you could set the
`SECRET_KEY`:

    # .env
    DJANGO_SECRET_KEY="very-secret-random-value-plz"

For a given DjangoKit setting, the env var name is the name of the
setting prefixed with `DJANGOKIT_`. For example, to set the package
name:

    DJANGOKIT_PACKAGE="myapp"

Database Settings
-----------------

Settings for the *default* cache & database can be specified using
special-case env vars::

    # .env.production
    DJANGO_CACHE_
    DJANGO_DATABASE_NAME="/production/path/to/db/sqlite.db"

Settings for other databases can be specified using the nested settings
syntax (see below).

Nested Settings
---------------

Cache, database, and logging settings are a special case due to nesting.
They can be defined using the following convention (note the double
underscores and case sensitivity):

    DJANGO_DATABASES_<name>__<key>__<subkey>

For example, to override the default database settings:

    # .env.production
    DJANGO_DATABASES_default__ENGINE="django.contrib.gis.db.backends.postgis"
    DJANGO_DATABASES_default__USER="some_user"
    DJANGO_DATABASES_default__PASSWORD="some_password"
    DJANGO_DATABASES_default__HOST="some.host"

Prepending and Appending Settings
---------------------------------

To prepend or append entries to the `INSTALLED_APPS`, `MIDDLEWARE`, and
other list settings, you can use the following form::

    DJANGO_PREPEND_INSTALLED_APPS=["my.app"]
    DJANGO_APPEND_MIDDLEWARE=["my.middleware"]

This allows the defaults to be modified without replacing them
completely, e.g. if you just need to add a single installed app.

Settings for Third Party Apps
----------------------------

Settings for third party Django apps can be specified via env vars too,
in the same manner as other Django settings::

    DJANGO_THIRD_PARTY_A="AAA"
    DJANGO_THIRD_PARTY_B="BBB"

Advanced Settings
-----------------

It's also possible to load settings from an additional settings module.
To do so, set the `DJANGO_ADDITIONAL_SETTINGS_MODULE` env var to point
at a settings module with additional settings.

These additional settings will override the defaults provided here but
any env settings will still take precedence.

"""
import socket
from dataclasses import asdict, dataclass, field, fields
from importlib import import_module
from itertools import chain
from os import environ
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Union
from uuid import uuid4

from django.conf import global_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .env import getenv, load_dotenv

# NOTE: If the DOTENV_FILE env var isn't set, this will fall back to
#       using a dotenv file in the current working directory. This is
#       fine in development, but in production it's usually better to
#       set DOTENV_FILE explicitly.
load_dotenv()


class DefaultSettings:
    """A bucket for the default settings."""

    def __init__(self, **kwargs):
        for name, val in kwargs.items():
            setattr(self, name, val)

    def __contains__(self, name):
        return name in self.__dict__

    def __getitem__(self, name):
        return self.__dict__[name]


@dataclass
class DjangoKitSettings:
    """DjangoKit settings.

    This defines the available DjangoKit settings, their types, and
    their default values. It also contains a number of attributes
    derived from the DjangoKit settings.

    """

    package: str
    """Top level package name of the DjangoKit app."""

    app_label: str
    """App label for the DjangoKit app (often the same as `package`)."""

    mount_point: str = ""
    """URL mount point for the DjangoKit app, relative to site root."""

    admin_prefix: str = "$admin/"
    """URL path to Django Admin, relative to site root."""

    api_prefix: str = "$api/"
    """URL path prefix for API routes, relative to site root."""

    page_prefix: str = ""
    """URL path prefix for page routes, relative to site root."""

    title: str = "A DjangoKit Site"
    """Site title (used for `<title>`)"""

    description: str = "A website made with DjangoKit"
    """Site description (used for `<meta name="description">`)"""

    global_stylesheets: List[str] = field(default_factory=lambda: ["global.css"])
    """Global stylesheets to be injected into the document `<head>`."""

    current_user_serializer: Union[
        str, Callable
    ] = "djangokit.core.user.current_user_serializer"
    """Serializer function used to serialize the current user."""

    ssr: bool = True
    """Whether SSR is enabled."""

    webmaster: str = field(default_factory=lambda: f"webmaster@{socket.gethostname()}")
    """Email address of the webmaster / site admin."""

    noscript_message: str = (
        "This site requires JavaScript to be enabled in your browser."
    )
    """Message to display when browser JS is disabled.
    
    Can be set to "" to disable showing a noscript message.
    
    """

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "package":
            package = value
            module = import_module(package)
            paths = module.__path__
            if len(paths) > 1:
                raise ImproperlyConfigured(
                    f"DjangoKit app package {package} appears to be a "
                    "namespace package because it resolves to multiple "
                    "file system paths. You might need to add an "
                    "__init__.py to the package."
                )
            package_dir = Path(paths[0])
            self.package_dir = package_dir
            self.app_dir = package_dir / "app"
            self.models_dir = package_dir / "models"
            self.routes_dir = package_dir / "routes"
            self.routes_package = f"{package}.routes"
            self.static_dir = package_dir / "static"
        elif name == "current_user_serializer":
            serializer = value
            if isinstance(serializer, str):
                self.current_user_serializer = import_string(serializer)

    def __contains__(self, name):
        return hasattr(self, name)

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, val):
        return setattr(self, name, val)

    def check(self):
        # Prefixes must be unique.
        for a, a_label, b, b_label in (
            (self.admin_prefix, "Admin", self.api_prefix, "API"),
            (self.admin_prefix, "Admin", self.page_prefix, "Page"),
            (self.api_prefix, "API", self.page_prefix, "Page"),
        ):
            if a == b:
                raise ImproperlyConfigured(
                    f"{b_label} prefix must be different from {a_label} prefix."
                )

        # Mount point & prefixes:
        # - can be an empty string
        # - must not be a single slash
        # - must not start with a slash
        # - must end with a slash
        for val, label in (
            (self.mount_point, "Mount point"),
            (self.admin_prefix, "Admin prefix"),
            (self.api_prefix, "API prefix"),
            (self.page_prefix, "Page prefix"),
        ):
            if not val:
                continue
            if val == "/":
                raise ImproperlyConfigured(
                    f"{label} is not valid (use an empty string instead of a slash)."
                )
            if val.startswith("/"):
                raise ImproperlyConfigured(f"{label} must not start with a slash.")
            if not val.endswith("/"):
                raise ImproperlyConfigured(f"{label} must end with a slash.")

    def as_dict(self) -> Dict[str, Any]:
        """Return a dict with *all* DjangoKit settings.

        This will include defaults plus any values set in the project's
        Django settings module in the `DJANGOKIT` dict.

        """
        return asdict(self)


debug = getenv("DJANGO_DEBUG", False, bool)
test = getenv("DJANGO_TEST", False, bool)
secret_key = f"INSECURE:{uuid4()}" if test else getenv("DJANGO_SECRET_KEY")

# Template settings
cached_loader = "django.template.loaders.cached.Loader"
template_loader = "djangokit.core.templates.loader.Loader"
template_loaders: List[Union[str, Tuple[str, List[str]]]] = (
    [template_loader] if debug else [(cached_loader, [template_loader])]
)

# NOTE: This only includes defaults that differ from Django's global
#       defaults. If a setting doesn't have a default here, Django's
#       global default will be used.
default_settings = DefaultSettings(
    # DjangoKit
    DJANGOKIT={},
    # Basics
    ROOT_URLCONF="djangokit.core.urls",
    SECRET_KEY=secret_key,
    WSGI_APPLICATION="djangokit.core.wsgi.application",
    # Localization
    TIME_ZONE="America/Los_Angeles",
    USE_TZ=True,
    # Apps
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ],
    # Middleware
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    # Databases
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    },
    # Auth
    LOGIN_URL="/login",
    AUTH_PASSWORD_VALIDATORS=[
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ],
    # Static files
    STATIC_ROOT="static",
    STATIC_URL="static/",
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    # Templates
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "loaders": template_loaders,
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
    # Logging
    LOGGING={
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "formatters": {
            "default": {
                "format": "[%(levelname)s] %(name)s %(message)s",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
)


settings = globals()


def import_additional_settings():
    """Import another settings module and add its settings.

    This is useful if the additional settings are complex and would be
    hard or impossible to specify as environment variables.

    .. note::
        Settings specified via environment variables will override
        settings specified in an additional settings module.

    """
    module_name = getenv("DJANGO_ADDITIONAL_SETTINGS_MODULE", None)
    if module_name:
        try:
            module = import_module(module_name)
        except ImportError:
            raise ImportError(
                "The additional Django settings module "
                f"`{module_name}`, which was specified via the "
                "DJANGO_ADDITIONAL_SETTINGS_MODULE environment "
                "variable, could not be imported. Check that the "
                "module path is correct and that all imports in the "
                "module are valid."
            )
        for name, val in vars(module).items():
            if name.isupper():
                settings[name] = val


def add_known_django_settings():
    """Add Django settings defined in the environment.

    If a Django setting isn't defined in the environment and has a
    default defined in `defaults`, the default will be used. Otherwise,
    the setting will be left unset (leaving it to be handled internally
    by Django).

    """
    # NOTE: ROOT_URLCONF is a special case because it isn't defined in
    #       Django's global settings
    for name in chain(vars(global_settings), ["ROOT_URLCONF"]):
        env_name = f"DJANGO_{name}"
        if env_name in environ:
            val = getenv(env_name)
            settings[name] = val
        elif name not in settings and name in default_settings:
            # TODO: Copy defaults so they aren't overwritten
            val = default_settings[name]
            settings[name] = val


def add_other_django_settings():
    """Add other Django settings defined in the environment.

    These can include:

    - Settings for third party Django apps
    - Default database settings
    - *Any* other settings -- any env var prefixed with `DJANGO_` will
      be added

    """
    known_settings = vars(global_settings)
    for env_name in environ:
        if env_name.startswith("DJANGO_"):
            name = env_name[7:]
            if name in known_settings or name == "ROOT_URLCONF":
                continue
            if name.startswith("CACHE_") and not name.startswith("CACHE_MIDDLEWARE_"):
                # Default cache settings
                caches = settings.setdefault("CACHES", {})
                setting = caches.setdefault("default", {})
                set_nested(setting, 1, "DJANGO_CACHE_", env_name)
            elif name.startswith("DATABASE_"):
                # Default database settings
                setting = settings["DATABASES"]["default"]
                set_nested(setting, 1, "DJANGO_DATABASE_", env_name)
            else:
                # Third party or other setting
                val = getenv(env_name)
                settings[name] = val


def add_nested_settings(name, min_path_len, env_prefix=None):
    """Process nested settings like CACHES, DATABASES, and LOGGING.

    The root setting (e.g., `DATABASES`) is expected to already exist,
    at least as an empty dict.

    After stripping the env prefix, the env var name is split on double
    underscores into segments corresponding to sub-dicts of the root
    setting. For each segment, a sub-dict is added if not already
    present.

    Args:
        name:
            The name of the setting (e.g. "DATABASES").

        env_prefix:
            The env prefix (e.g., "DJANGO_DATABASES_")

    For example, consider the following .env file::

        # .env.production
        DJANGO_DATABASES_default__HOST="some.host"

    Calling `add_nested_setting("DATABASES", 2)` will set
    `DATABASES["default"]["HOST"] = "some.host"`.

    """
    env_prefix = env_prefix or f"DJANGO_{name}_"
    if name in settings:
        top_level_setting = settings[name]
    else:
        default = getattr(global_settings, name, {})
        top_level_setting = settings[name] = default
    for env_name in environ:
        if env_name.startswith(env_prefix):
            set_nested(top_level_setting, min_path_len, env_prefix, env_name)


def set_nested(setting, min_path_len, env_prefix, env_name):
    """Set a sub-setting of the specified setting.

    The setting can be a top level setting such as `DATABASES` or a
    nested setting such as `DATABASES["default"]`.

    Example::

        setting = settings.DATABASES["default"]
        env_prefix = "DJANGO_DATABASE_"
        env_name = "DJANGO_DATABASE_NAME"
        _set_nested(setting, 1, env_prefix, env_name)
        # -> sets DATABASES["default"]["NAME"]

    Example::

        setting = settings.DATABASES
        env_prefix = "DJANGO_DATABASES_"
        env_name = "DJANGO_DATABASE_default__NAME"
        _set_nested(setting, 2, env_prefix, env_name)
        # -> sets DATABASES["default"]["NAME"]

    """
    path = env_name[len(env_prefix) :]
    segments = path.split("__")
    num_segments = len(segments)
    if num_segments < min_path_len:
        raise ImproperlyConfigured(
            f"Env setting name is not valid: {env_name}. Expected "
            f"{min_path_len} segments separated by __."
        )
    val = getenv(env_name)
    if num_segments == 1:
        setting[segments[0]] = val
    else:
        obj = setting[segments[0]]
        for segment in segments[1:-1]:
            obj = obj.setdefault(segment, {})
        obj[segments[-1]] = val


def prepend_settings():
    for prepend_name, prepend_val in settings.items():
        if prepend_name.startswith("PREPEND_"):
            name = prepend_name[8:]
            current_val = settings[name]
            settings[name] = prepend_val + current_val


def append_settings():
    for append_name, append_val in settings.items():
        if append_name.startswith("APPEND_"):
            name = append_name[7:]
            current_val = settings[name]
            settings[name] = current_val + append_val


def add_djangokit_settings():
    """Add DjangoKit settings defined in the environment.

    This also:

    - Adds the app's package and "djangokit.core" to the front of
      `INSTALLED_APPS`.

    - Adds the DjangoKit middleware to the end of `MIDDLEWARE`.

    """
    dk_settings = settings.setdefault("DJANGOKIT", default_settings.DJANGOKIT).copy()

    for f in fields(DjangoKitSettings):
        name = f.name
        env_name = f"DJANGOKIT_{name.upper()}"
        if env_name in environ:
            val = getenv(env_name)
            dk_settings[name] = val

    has_app_label = "app_label" in dk_settings
    if not has_app_label:
        dk_settings["app_label"] = ""

    try:
        dk_settings = DjangoKitSettings(**dk_settings)
    except Exception as exc:
        raise ImproperlyConfigured(exc)

    package = dk_settings.package
    settings["DJANGOKIT"] = dk_settings

    if not has_app_label:
        dk_settings.app_label = package.replace(".", "_")

    installed_apps = settings["INSTALLED_APPS"]
    settings["INSTALLED_APPS"] = [package, "djangokit.core"] + installed_apps

    middleware = settings["MIDDLEWARE"]
    settings["MIDDLEWARE"] = middleware + [
        "djangokit.core.middleware.djangokit_middleware"
    ]

    dk_settings.check()


import_additional_settings()
add_known_django_settings()
add_other_django_settings()
add_nested_settings("CACHES", 2)
add_nested_settings("DATABASES", 2)
if not isinstance(settings.get("LOGGING"), str):
    add_nested_settings("LOGGING", 1)
prepend_settings()
append_settings()

# NOTE: The ordering of this matters because it adds the app's package
#       name to the front of INSTALLED_APPS.
add_djangokit_settings()
