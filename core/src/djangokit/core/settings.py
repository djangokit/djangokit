# Default settings used by DjangoKit projects.
from uuid import uuid4

from .env import djangokit_settings_from_env, getenv, load_dotenv

load_dotenv()

DEBUG = getenv("DJANGO_DEBUG", False)
TEST = getenv("DJANGO_TEST", False)

DJANGOKIT = djangokit_settings_from_env()

if TEST:
    SECRET_KEY = f"INSECURE-KEY-USED-IN-TEST-MODE-ONLY-{uuid4()}"
else:
    SECRET_KEY = getenv("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", [])
ROOT_URLCONF = getenv("DJANGO_ROOT_URLCONF", f"djangokit.core.urls")
WSGI_APPLICATION = getenv("DJANGO_WSGI_APPLICATION", f"djangokit.core.wsgi.application")

LANGUAGE_CODE = getenv("DJANGO_LANGUAGE_CODE", "en-us")
TIME_ZONE = getenv("DJANGO_TIME_ZONE", "America/Los_Angeles")
USE_I18N = getenv("DJANGO_USE_I18N", True)
USE_TZ = getenv("DJANGO_USE_TZ", True)

INSTALLED_APPS = [
    DJANGOKIT["package"],
    "djangokit.core",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "djangokit.core.middleware.djangokit_middleware",
]

STATIC_ROOT = getenv("DJANGO_STATIC_ROOT", "static")
STATIC_URL = getenv("DJANGO_STATIC_URL", "static/")

app_dirs_loader = "django.template.loaders.app_directories.Loader"
cached_loader = "django.template.loaders.cached.Loader"
template_loaders = [app_dirs_loader] if DEBUG else [(cached_loader, [app_dirs_loader])]

TEMPLATES = [
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
]

DATABASES = {
    "default": {
        "ENGINE": getenv(
            "DJANGO_DATABASES_DEFAULT_ENGINE", "django.db.backends.sqlite3"
        ),
        "USER": getenv("DJANGO_DATABASES_DEFAULT_USER", ""),
        "PASSWORD": getenv("DJANGO_DATABASES_DEFAULT_PASSWORD", ""),
        "HOST": getenv("DJANGO_DATABASES_DEFAULT_HOST", ""),
        "PORT": getenv("DJANGO_DATABASES_DEFAULT_PORT", ""),
        "NAME": getenv("DJANGO_DATABASES_DEFAULT_NAME", "db.sqlite3"),
        "ATOMIC_REQUESTS": getenv("DJANGO_DATABASES_DEFAULT_ATOMIC_REQUESTS", False),
        "AUTOCOMMIT": getenv("DJANGO_DATABASES_DEFAULT_AUTOCOMMIT", True),
        "TIME_ZONE": getenv("DJANGO_DATABASES_DEFAULT_TIME_ZONE", None),
        "CONN_MAX_AGE": getenv("DJANGO_DATABASES_DEFAULT_CONN_MAX_AGE", 0),
        "CONN_HEALTH_CHECKS": getenv(
            "DJANGO_DATABASES_DEFAULT_CONN_HEALTH_CHECKS", False
        ),
    }
}

DEFAULT_AUTO_FIELD = getenv(
    "DJANGO_DEFAULT_AUTO_FIELD", "django.db.models.BigAutoField"
)

LOGIN_URL = getenv("DJANGO_LOGIN_URL", "/login")

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
