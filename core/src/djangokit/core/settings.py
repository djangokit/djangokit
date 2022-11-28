"""Default settings used by DjangoKit projects.

Settings are set via environment variables in a project's `.env` file(s)
and/or using standard OS mechanisms.

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

Database settings are a special case due to nesting. They can be defined
using the following convention (note the double underscores):

    DJANGO_DATABASES_<name>__<key>__<subkey>

For example, to override the default database settings:

    # .env
    DJANGO_DATABASES_DEFAULT__ENGINE="django.contrib.gis.db.backends.postgis"
    DJANGO_DATABASES_DEFAULT__USER="some_user"
    DJANGO_DATABASES_DEFAULT__PASSWORD="some_password"
    DJANGO_DATABASES_DEFAULT__HOST="some.host"

.. todo:
    Support DATABASE_URL? It might be possible to use the
    django-database-url package for this.

"""
from os import environ
from uuid import uuid4

from django.conf import global_settings
from django.core.exceptions import ImproperlyConfigured

from .env import getenv, load_dotenv

load_dotenv()


class Settings:

    required = object()

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

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
        "package": djangokit_package,
        "app_label": djangokit_package.replace(".", "_"),
        "global_css": ["global.css"],
        "current_user_serializer": "djangokit.core.user.current_user_serializer",
        "ssr": True,
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
)

DJANGOKIT = defaults.DJANGOKIT.copy()

# XXX: This is a special case because ROOT_URLCONF isn't defined in
#      Django's global settings.
ROOT_URLCONF = getenv("DJANGO_ROOT_URLCONF", defaults.ROOT_URLCONF)

settings = globals()

# Find any DjangoKit settings defined in the environment and add them to
# the local settings.
for name in defaults.DJANGOKIT:
    env_name = f"DJANGOKIT_{name.upper()}"
    if env_name in environ:
        value = getenv(env_name)
        DJANGOKIT[name] = value


# Find any Django settings defined in the environment and add them to
# the local settings. If a setting isn't defined in the environment and
# has a default defined above, the default will be used. Otherwise, the
# setting will be left unset (leaving it Do be handled internally by
# Django).
for name in vars(global_settings):
    env_name = f"DJANGO_{name}"
    if env_name in environ:
        value = getenv(env_name)
        settings[name] = value
    elif name in defaults:
        value = defaults[name]
        settings[name] = value

# Process nested database settings.
db_settings = settings["DATABASES"]
prefix = "DJANGO_DATABASES_"
prefix_len = len(prefix)
for env_name in environ:
    if not env_name.startswith(prefix):
        continue

    path = env_name[prefix_len:]
    segments = path.split("__")
    num_segments = len(segments)

    if num_segments < 2:
        raise ImproperlyConfigured(
            f"Database setting name is not valid: {env_name}. "
            "Expected format is DJANGO_DATABASES_<key>={...} or"
            "DJANGO_DATABASES_<key>__<subkey>=<value>."
        )

    db_key = segments[0].lower()  # e.g. default
    db_settings.setdefault(db_key)

    obj = db_settings[db_key]
    for segment in segments[1:-1]:
        obj = obj.setdefault(segment, {})
    value = getenv(env_name)
    obj[segments[-1]] = value
