"""Default Django settings module used by DjangoKit projects.

There are several default settings defined below.

Env-specific settings are loaded from TOML files with `django` and
`djangokit` sections::

    # settings.public.toml
    [django]
    DATABASES.default.ENGINE = "django.db.backends.postgresql"
    DATABASES.default.NAME = "my_database"

    [djangokit]
    package = "my_package"

    # settings.development.toml
    [django]
    SECRET_KEY = "super secret"
    DATABASES.default.PASSWORD = "my_database_password"

The public settings file SHOULD NOT contain any sensitive settings and
MAY be committed to version control.

The env-specific settings file MAY contain sensitive settings and SHOULD
NOT be committed to version control.

The env-specific settings are MERGED into the public settings which are
MERGED into the base settings.

Additional Django Settings Module
---------------------------------

It's also possible to load settings from an additional Django settings
module. To do so, set the `DJANGO_ADDITIONAL_SETTINGS_MODULE` env var to
point at a settings module with additional settings. The specified
module will be loaded and its settings MERGED into the base settings.

These additional settings will override the base settings below but any
env-specific settings will take precedence.

The purpose of this additional settings file is to provide a hook for
specialized settings loading. For example, if you need to load the
secret key, database password, etc settings from a secrets manager, the
additional settings module would be a good place to do that.

Prepending and Appending Settings
---------------------------------

To prepend or append entries to the `INSTALLED_APPS`, `MIDDLEWARE`, and
other list settings, you can use the following form::

    PREPEND_INSTALLED_APPS = ["my.app"]
    APPEND_MIDDLEWARE = ["my.middleware"]

This allows the base settings to be modified without replacing them
completely, e.g. if you just need to add a single installed app.

Environment Variable Settings
-----------------------------

You can specify that a setting should be loaded from an environment
variable by adding it to the `[django.from_env]` and/or
`[djangokit.from_env]` sections of your settings file (usually in the
`settings.public.toml` file).

The values of such settings will be converted from TOML if possible.
Example::

    # settings.public.toml
    [django.from_env]
    API_KEY = "DJANGO_API_KEY"
    DATABASES.default.NAME = "DJANGO_DATABASE_NAME"

Note that if `API_KEY` isn't set in the Django settings module or file
that the `DJANGO_API_KEY` env var will be *required* and an error will
be raised if it's not set.

Some settings will always be loaded from env vars, if they're present in
the environment:

# Django setting name/path loaded from env var name
- `DEBUG` = `DJANGO_DEBUG`
- `SECRET_KEY` = `DJANGO_SECRET_KEY`
- `DATABASES.default.HOST` = `DJANGO_DATABASE_HOST`
- `DATABASES.default.PASSWORD` = `DJANGO_DATABASE_PASSWORD`

.. todo:: Add other known sensitive settings?

"""

from importlib import import_module
from os import environ
from typing import Any, Dict

from django.core.exceptions import ImproperlyConfigured

from .conf import getenv, load_settings
from .dk_settings import DjangoKitSettings
from .utils import merge_dicts

# Default Settings -----------------------------------------------------

# DjangoKit
DJANGOKIT: Dict[str, Any] = {}

# Basics
ENV = "development"
DEBUG = False
ROOT_URLCONF = "djangokit.core.urls"
WSGI_APPLICATION = "djangokit.core.wsgi.application"

# Localization
TIME_ZONE = "America/Los_Angeles"
USE_TZ = True

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Databases
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

# Auth
LOGIN_URL = "/login"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": name}
    for name in (
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "django.contrib.auth.password_validation.MinimumLengthValidator",
        "django.contrib.auth.password_validation.CommonPasswordValidator",
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    )
]

# Static files
STATIC_ROOT = "static"
STATIC_URL = "static/"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            # NOTE: Default loaders option is derived below
            "loaders": None,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Logging
LOGGING = {
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
    "loggers": {
        # NOTE: Default logger for package is derived below
    },
}

# END Default Settings -------------------------------------------------


settings = globals()

# These settings will always be loaded from environment variables, if
# the corresponding env vars are set.
default_django_settings_from_env = {
    "DEBUG": "DJANGO_DEBUG",
    "SECRET_KEY": "DJANGO_SECRET_KEY",
    "DATABASES": {
        "default": {
            "HOST": "DJANGO_DATABASE_HOST",
            "USER": "DJANGO_DATABASE_USER",
            "PASSWORD": "DJANGO_DATABASE_PASSWORD",
            "NAME": "DJANGO_DATABASE_NAME",
        }
    },
}

# These dicts will be populated when the settings file is read in
# merge_loaded_settings().
django_settings_from_env = {}
djangokit_settings_from_env = {}


def merge_additional_settings_module():
    """Merge settings loaded from additional Django settings file."""
    name = "DJANGO_ADDITIONAL_SETTINGS_MODULE"
    if name in environ:
        additional_settings_module_name = environ[name]
        additional_settings_module = import_module(additional_settings_module_name)
        settings.update(merge_dicts(settings, vars(additional_settings_module)))


def merge_loaded_settings():
    """Merge settings loaded from TOML settings file."""
    # Load settings from file(s).
    loaded_settings = load_settings()

    # Merge loaded Django settings into base settings.
    django_settings = loaded_settings.get("django", {})
    if "from_env" in django_settings:
        django_settings_from_env.update(django_settings["from_env"])
    django_settings = {n: v for n, v in django_settings.items() if n.isupper()}
    settings.update(merge_dicts(settings, django_settings))

    # Merge loaded DjangoKit settings into base settings.
    dk_settings = loaded_settings.get("djangokit", {})
    dk_settings.pop("cli", None)
    if "from_env" in dk_settings:
        djangokit_settings_from_env.update(dk_settings["from_env"])
    settings["DJANGOKIT"].update(merge_dicts(settings["DJANGOKIT"], dk_settings))


def merge_env_settings():
    traverse_from_env_dict(settings, default_django_settings_from_env, False)
    traverse_from_env_dict(settings, django_settings_from_env, True)
    traverse_from_env_dict(
        settings["DJANGOKIT"],
        djangokit_settings_from_env,
        True,
        "DJANGOKIT",
    )


def traverse_from_env_dict(settings_dict, from_env_dict, required, parent_path=None):
    # Traverse the from-env dict, which should have the same structure
    # as the global settings dict, recursively descending into
    # sub-dicts. When a leaf is reached--an env var name--the env var
    # will be used as the value of the setting or sub-setting.
    for segment, env_name_or_subdict in from_env_dict.items():
        if isinstance(env_name_or_subdict, str):
            env_name = env_name_or_subdict
            if env_name in environ:
                # If the env var is present, use it regardless of
                # whether it's required.
                settings_dict[segment] = getenv(env_name, required=True)
            elif required and segment not in settings_dict:
                # If the env var is NOT present but is required AND
                # doesn't have a default value in the settings, that's
                # an error.
                path = f"{parent_path}.{segment}" if parent_path else segment
                raise ImproperlyConfigured(
                    "Expected environment variable to be set for "
                    f"setting {path}: {env_name}"
                )
        elif isinstance(env_name_or_subdict, dict):
            traverse_from_env_dict(
                settings_dict.setdefault(segment, {}),
                env_name_or_subdict,
                required,
                f"{parent_path}.{segment}" if parent_path else segment,
            )
        else:
            type_ = type(env_name_or_subdict)
            val = env_name_or_subdict
            raise ImproperlyConfigured(
                f"Expected str or dict but got {type_}: {val!r}."
            )


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
    """Add DjangoKit settings.


    - Converts `DJANGOKIT` setting to an instance of
      :class:`DjangoKitSettings`.
    - Adds the app's package and "djangokit.core" to the front of
      `INSTALLED_APPS`.
    - Adds the DjangoKit middleware to the end of `MIDDLEWARE`.
    - Adds template loader option to `TEMPLATES[0]["OPTIONS"]`.
    - Checks the DjangoKit settings to ensure they're valid.

    """
    dk_settings = settings.setdefault("DJANGOKIT", {})

    if "app_label" not in dk_settings:
        package = dk_settings.get("package")
        if package:
            dk_settings["app_label"] = package.replace(".", "_")

    try:
        dk_settings = DjangoKitSettings(**dk_settings)
    except Exception as exc:
        raise ImproperlyConfigured(exc)

    package = dk_settings.package
    settings["DJANGOKIT"] = dk_settings

    installed_apps = settings["INSTALLED_APPS"]
    settings["INSTALLED_APPS"] = [package, "djangokit.core"] + installed_apps

    middleware = settings["MIDDLEWARE"]
    settings["MIDDLEWARE"] = middleware + [
        "djangokit.core.middleware.djangokit_middleware"
    ]

    dk_settings.check()


def set_derived_settings():
    """Set defaults for settings that are derived from other settings.

    If a setting is already set, this has no effect.

    """
    env = settings["ENV"]
    debug = settings["DEBUG"]
    package = settings["DJANGOKIT"].package

    # Set default template loaders option
    template_options = settings["TEMPLATES"][0]["OPTIONS"]
    loaders = template_options.get("loaders")
    if loaders is None:
        template_loader = "djangokit.core.templates.loader.Loader"
        if debug:
            template_options["loaders"] = [template_loader]
        else:
            cached_loader = "django.template.loaders.cached.Loader"
            template_options["loaders"] = [(cached_loader, [template_loader])]

    log_settings = settings["LOGGING"]
    if env == "test":
        log_settings["disable_existing_loggers"] = True
    else:
        # Set default logging options for app package
        loggers = log_settings.setdefault("loggers", {})
        package_logger = loggers.get(package)
        if package_logger is None:
            loggers[package] = {
                "level": "DEBUG" if debug else "INFO",
            }


merge_additional_settings_module()
merge_loaded_settings()
merge_env_settings()
prepend_settings()
append_settings()

# NOTE: The ordering of this matters because it adds the app's package
#       name to the front of INSTALLED_APPS and the DjangoKit middleware
#       to the end of MIDDLEWARE.
add_djangokit_settings()

set_derived_settings()
