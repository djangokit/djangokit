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

Settings for the *default* database can be specified using special-case
env vars::

    # .env.production
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
import importlib
from itertools import chain
from os import environ
from typing import List, Tuple, Union
from uuid import uuid4

from django.conf import global_settings
from django.core.exceptions import ImproperlyConfigured

from .conf import KNOWN_SETTINGS
from .env import getenv, load_dotenv

load_dotenv()


class Settings:

    required = object()

    def __init__(self, **kwargs):
        for name, val in kwargs.items():
            setattr(self, name, val)

    def __contains__(self, name):
        return name in self.__dict__

    def __getitem__(self, name):
        return self.__dict__[name]


djangokit_package = getenv("DJANGOKIT_PACKAGE")


def get_djangokit_settings():
    # XXX: Keep in sync with :data:`.conf.KNOWN_SETTINGS`.
    dk_settings = {
        "package": djangokit_package,
        "app_label": djangokit_package.replace(".", "_"),
    }
    for name in KNOWN_SETTINGS:
        known = KNOWN_SETTINGS[name]
        if "default" in known:
            dk_settings[name] = known["default"]
    return dk_settings


debug = getenv("DJANGO_DEBUG", False, bool)
test = getenv("DJANGO_TEST", False, bool)
secret_key = f"INSECURE:{uuid4()}" if test else getenv("DJANGO_SECRET_KEY")
app_dirs_loader = "django.template.loaders.app_directories.Loader"

prepend_installed_apps = getenv("DJANGO_PREPEND_INSTALLED_APPS", [])
append_installed_apps = getenv("DJANGO_APPEND_INSTALLED_APPS", [])

prepend_middleware = getenv("DJANGO_PREPEND_MIDDLEWARE", [])
append_middleware = getenv("DJANGO_APPEND_MIDDLEWARE", [])

cached_loader = "django.template.loaders.cached.Loader"
template_loaders: List[Union[str, Tuple[str, List[str]]]] = (
    [app_dirs_loader] if debug else [(cached_loader, [app_dirs_loader])]
)


# NOTE: This only includes defaults that differ from Django's global
#       defaults. If a setting doesn't have a default here, Django's
#       global default will be used.
defaults = Settings(
    # DjangoKit
    DJANGOKIT=get_djangokit_settings(),
    # Basics
    ROOT_URLCONF="djangokit.core.urls",
    SECRET_KEY=secret_key,
    WSGI_APPLICATION="djangokit.core.wsgi.application",
    # Localization
    TIME_ZONE="America/Los_Angeles",
    USE_TZ=True,
    # Apps
    INSTALLED_APPS=(
        prepend_installed_apps
        + [
            djangokit_package,
            "djangokit.core",
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ]
        + append_installed_apps
    ),
    # Middleware
    MIDDLEWARE=(
        prepend_middleware
        + [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            "djangokit.core.middleware.djangokit_middleware",
        ]
        + append_middleware
    ),
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
            module = importlib.import_module(module_name)
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


def add_djangokit_settings():
    """Add DjangoKit settings defined in the environment."""
    if "DJANGOKIT" not in settings:
        settings["DJANGOKIT"] = defaults.DJANGOKIT.copy()
    for name in defaults.DJANGOKIT:
        env_name = f"DJANGOKIT_{name.upper()}"
        if env_name in environ:
            val = getenv(env_name)
            settings["DJANGOKIT"][name] = val


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
        elif name not in settings and name in defaults:
            # TODO: Copy defaults so they aren't overwritten
            val = defaults[name]
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
                _set_nested(setting, 1, "DJANGO_CACHE_", env_name)
            elif name.startswith("DATABASE_"):
                # Default database settings
                setting = settings["DATABASES"]["default"]
                _set_nested(setting, 1, "DJANGO_DATABASE_", env_name)
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

    This will set `DATABASES["default"]["HOST"] = "some.host"`.

    .. note::

    """
    env_prefix = env_prefix or f"DJANGO_{name}_"
    if name in settings:
        top_level_setting = settings[name]
    else:
        default = getattr(global_settings, name, {})
        top_level_setting = settings[name] = default
    for env_name in environ:
        if env_name.startswith(env_prefix):
            _set_nested(top_level_setting, min_path_len, env_prefix, env_name)


def _set_nested(setting, min_path_len, env_prefix, env_name):
    """Set a sub-setting of the specified setting.

    The setting can be a top level setting such as `DATABASES` or a
    nested setting such as `DATABASES["default"]`.

    Example::

        setting = settings.DATABASES["default"]
        env_prefix = "DJANGO_DATABASE_"
        env_name = "DJANGO_DATABASE_NAME"
        _set_nested(setting, env_prefix, env_name)
        # -> sets DATABASES["default"]["NAME"]

    Example::

        setting = settings.DATABASES
        env_prefix = "DJANGO_DATABASES_"
        env_name = "DJANGO_DATABASE_default__NAME"
        _set_nested(setting, env_prefix, env_name)
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


import_additional_settings()
add_djangokit_settings()
add_known_django_settings()
add_other_django_settings()
add_nested_settings("CACHES", 2)
add_nested_settings("DATABASES", 2)

if not isinstance(settings.get("LOGGING"), str):
    # XXX: Assume that LOGGING_CONFIG="logging.config.fileConfig" and
    #      LOGGING is a log config file path.
    #
    # TODO: Make this more robust.
    add_nested_settings("LOGGING", 1)
