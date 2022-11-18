from pathlib import Path

ROOT_URLCONF = "djangokit.core.test.urls"

DJANGOKIT = {
    "package": "djangokit.core.test",
}

INSTALLED_APPS = [
    "djangokit.core",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(__file__).parent / "db.sqlite3",
    }
}
