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


def getenv(name: str, default: Any = NOT_SET, expected_type: type = NOT_SET) -> Any:
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
    else:
        return default

    value = convert_env_val(value)

    if expected_type is not NOT_SET:
        if not isinstance(value, expected_type):
            expected_type_name = expected_type.__name__
            type_name = value.__class__.__name__
            raise ImproperlyConfigured(
                f"Setting {name} has incorrect type. Expected "
                f"{expected_type_name}; got {type_name}."
            )

    return value


def convert_env_val(value: str) -> Any:
    try:
        value = json.loads(value)
    except ValueError:
        pass
    return value
