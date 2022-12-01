"""Default Django settings module used by DjangoKit projects.

Settings can be set via environment variables in a project's `.env`
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

Nested Settings
---------------

Cache and database settings are a special case due to nesting. They can
be defined using the following convention (note the double underscores
and case sensitivity):

    DJANGO_DATABASES_<name>__<key>__<subkey>

For example, to override the default database settings:

    # .env
    DJANGO_DATABASES_default__ENGINE="django.contrib.gis.db.backends.postgis"
    DJANGO_DATABASES_default__USER="some_user"
    DJANGO_DATABASES_default__PASSWORD="some_password"
    DJANGO_DATABASES_default__HOST="some.host"

.. todo:
    Support DATABASE_URL? It might be possible to use the
    django-database-url package for this.

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
from os import environ
from uuid import uuid4

from django.conf import global_settings
from django.core.exceptions import ImproperlyConfigured

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
debug = getenv("DJANGO_DEBUG", False, bool)
test = getenv("DJANGO_TEST", False, bool)
secret_key = f"INSECURE:{uuid4()}" if test else getenv("DJANGO_SECRET_KEY")
app_dirs_loader = "django.template.loaders.app_directories.Loader"
cached_loader = "django.template.loaders.cached.Loader"
template_loaders = [app_dirs_loader] if debug else [(cached_loader, [app_dirs_loader])]


# NOTE: This only includes defaults that differ from Django's global
#       defaults. If a setting doesn't have a default here, Django's
#       global default will be used.
defaults = Settings(
    # DjangoKit
    # XXX: Keep in sync with `.conf.Settings.known_settings`.
    DJANGOKIT={
        "title": "A DjangoKit Site",
        "description": "A website made with DjangoKit",
        "package": djangokit_package,
        "app_label": djangokit_package.replace(".", "_"),
        "global_css": ["global.css"],
        "current_user_serializer": "djangokit.core.user.current_user_serializer",
        "ssr": True,
        "webmaster": "",
        "static_build_dir": "",
    },
    # Basics
    ROOT_URLCONF="djangokit.core.urls",
    SECRET_KEY=secret_key,
    WSGI_APPLICATION="djangokit.core.wsgi.application",
    # Localization
    TIME_ZONE="America/Los_Angeles",
    USE_TZ=True,
    # Apps
    INSTALLED_APPS=[
        djangokit_package,
        "djangokit.core",
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
        "djangokit.core.middleware.djangokit_middleware",
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
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
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
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
)

DJANGOKIT = defaults.DJANGOKIT.copy()

# XXX: This is a special case because ROOT_URLCONF isn't defined in
#      Django's global settings.
ROOT_URLCONF = getenv("DJANGO_ROOT_URLCONF", defaults.ROOT_URLCONF)

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
    for name in defaults.DJANGOKIT:
        env_name = f"DJANGOKIT_{name.upper()}"
        if env_name in environ:
            val = getenv(env_name)
            DJANGOKIT[name] = val


def add_django_settings():
    """Add Django settings defined in the environment.

    If a Django setting isn't defined in the environment and has a
    default defined in `defaults`, the default will be used. Otherwise,
    the setting will be left unset (leaving it to be handled internally
    by Django).

    """
    for name in vars(global_settings):
        env_name = f"DJANGO_{name}"
        if env_name in environ:
            val = getenv(env_name)
            settings[name] = val
        elif name in defaults:
            val = defaults[name]
            settings[name] = val


def process_nested_settings(name, env_prefix=None):
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

    For example, onsider the following .env file::

        # .env
        DJANGO_DATABASES_default__HOST="some.host"

    This will set `DATABASES["default"]["HOST"] = "some.host"`.

    .. note::

    """
    if name in settings:
        root_setting = settings[name]
    else:
        default = getattr(global_settings, name, {})
        root_setting = settings[name] = default

    env_prefix = env_prefix or f"DJANGO_{name}_"
    env_prefix_len = len(env_prefix)

    for env_name in environ:
        if not env_name.startswith(env_prefix):
            continue

        path = env_name[env_prefix_len:]
        segments = path.split("__")
        num_segments = len(segments)

        if num_segments < 2:
            raise ImproperlyConfigured(
                f"Database setting name is not valid: {env_name}. "
                "Expected format is {env_prefix}<key>={...} or"
                "{env_prefix}<key>__<subkey>=<value>."
            )

        key = segments[0]
        root_setting.setdefault(key)

        setting = root_setting[key]
        for segment in segments[1:-1]:
            setting = setting.setdefault(segment, {})
        val = getenv(env_name)
        setting[segments[-1]] = val


import_additional_settings()
add_djangokit_settings()
add_django_settings()
process_nested_settings("CACHES")
process_nested_settings("DATABASES")
process_nested_settings("LOGGING")
