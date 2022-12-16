import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import dotenv
from django.core.exceptions import ImproperlyConfigured

log = logging.getLogger(__name__)

NotSet = type("NotSet", (), {})
NOT_SET = NotSet()


def get_dotenv_file(*, path=None, env=None) -> Path:
    """Figure out which .env file to use.

    If `path` is specified, use that. Otherwise:

    1. If `env` is specified, use `./.env.{env}`
    2. If the `DOTENV_FILE` env var is set, use it
    3. If the `ENV` env var is set, use `./.env.${ENV}`
    4. Fall back to `./.env`

    """
    if path is None:
        if env is not None:
            path = f".env.{env}"
            log.warning("Using .env file derived from env arg: %s", path)
        elif "DOTENV_FILE" in os.environ:
            path = os.environ["DOTENV_FILE"]
        elif "ENV" in os.environ:
            path = f".env.{os.environ['ENV']}"
            log.warning("Using .env file derived from ENV: %s", path)
        else:
            path = ".env"
            log.warning("Using default .env file: %s", path)
    return Path(path)


def load_dotenv(*, path=None, env=None) -> bool:
    """Load settings from .env file into environ.

    See :func:`get_dotenv_file` for details on dotenv file discovery.

    """
    path = get_dotenv_file(path=path, env=env)
    public_path = path.parent / ".env.public"
    if public_path.exists():
        public_loaded = dotenv.load_dotenv(public_path)
    else:
        public_loaded = False
    if path.exists():
        loaded = dotenv.load_dotenv(path)
    else:
        loaded = False
    return public_loaded or loaded


def get_dotenv_settings(*, path=None, env=None, convert=True) -> Dict[str, Any]:
    """Load settings from .env file into environ.

    By default, the values will be parsed as JSON.

    See :func:`get_dotenv_file` for details on dotenv file discovery.

    """
    path = get_dotenv_file(path=path, env=env)
    public_path = path.parent / ".env.public"
    values = {}
    if public_path.exists():
        values.update(dotenv.dotenv_values(public_path))
    if path.exists():
        values.update(dotenv.dotenv_values(path))
    if convert:
        return {n: convert_env_val(v) for n, v in values.items()}
    return values


def getenv(name: str, default=NOT_SET, expected_type: type = NotSet) -> Any:
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

    if expected_type is not NotSet:
        if not isinstance(value, expected_type):
            expected_type_name = expected_type.__name__
            type_name = value.__class__.__name__
            raise ImproperlyConfigured(
                f"Setting {name} has incorrect type. Expected "
                f"{expected_type_name}; got {type_name}."
            )

    return value


def convert_env_val(val: Optional[str]) -> Any:
    if val is None:
        return None
    try:
        val = json.loads(val)
    except ValueError:
        pass
    return val
