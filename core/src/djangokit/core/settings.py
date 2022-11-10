import json
import os
from typing import Any, Dict, Optional

import dotenv

NOT_SET = object()


def load_dotenv(path=".env") -> bool:
    """Load settings from .env file into environ."""
    return dotenv.load_dotenv(path)


def dotenv_values(path=".env") -> Dict[str, Optional[str]]:
    """Load settings from .env file into environ."""
    values = dotenv.dotenv_values(path)
    processed_values = {}
    for name, value in values.items():
        processed_values[name] = convert_value(value)
    return processed_values


def getenv(name: str, default: Any = NOT_SET) -> Any:
    """Get setting from environ."""
    if default is NOT_SET:
        value = os.environ[name]
    elif name in os.environ:
        value = os.environ[name]
        value = convert_value(value)
    else:
        value = default
    return value


def convert_value(value: str) -> Any:
    try:
        value = json.loads(value)
    except ValueError:
        pass
    return value
