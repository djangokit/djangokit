import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import dotenv
from django.core.exceptions import ImproperlyConfigured

NOT_SET = object()


def load_dotenv(path=".env") -> bool:
    """Load settings from .env file into environ."""
    path = Path(path)
    public_path = path.parent / ".env.public"
    dotenv.load_dotenv(public_path)
    return dotenv.load_dotenv(path)


def dotenv_settings(path=".env") -> Dict[str, Optional[str]]:
    """Load settings from .env file into environ."""
    path = Path(path)
    public_path = path.parent / ".env.public"
    values = dotenv.dotenv_values(public_path)
    values.update(dotenv.dotenv_values(path))
    processed_values = {}
    for name, value in values.items():
        processed_values[name] = convert_env_val(value)
    return processed_values


def getenv(name: str, default: Any = NOT_SET) -> Any:
    """Get setting from environment.

    If no default is specified, the setting *must* be present in the
    environment.

    """
    if default is NOT_SET:
        try:
            value = os.environ[name]
        except KeyError:
            raise ImproperlyConfigured(
                f"Expected environment variable to be set: {name}"
            )
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


def djangokit_settings_from_env():
    package = getenv("DJANGOKIT_PACKAGE")
    return {
        "package": package,
        "app_label": getenv("DJANGOKIT_APP_LABEL", package.replace(".", "_")),
        "global_css": getenv("DJANGOKIT_GLOBAL_CSS", ["global.css"]),
        "serialize_current_user": getenv(
            "DJANGOKIT_SERIALIZE_CURRENT_USER",
            "djangokit.core.user.serialize_current_user",
        ),
    }
