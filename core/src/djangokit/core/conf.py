import os
from pathlib import Path
from typing import Any

import toml
from django.core.exceptions import ImproperlyConfigured

from .utils import merge_dicts


def get_settings_file(*, path=None, env=None):
    """Figure out which settings file to use.

    If `path` is specified, use that. Otherwise:

    1. If `env` is specified, use `./settings.{env}.toml`
    2. If the `DJANGO_SETTINGS_FILE` env var is set, use it
    3. If the `ENV` env var is set, use `./settings.${ENV}.toml`
    4. Fall back to `./settings.toml`

    """
    if path is None:
        if env is not None:
            path = f"settings.{env}.toml"
        elif "DJANGO_SETTINGS_FILE" in os.environ:
            path = os.environ["DJANGO_SETTINGS_FILE"]
        elif "ENV" in os.environ:
            env = os.environ["ENV"]
            path = f"settings.{env}.toml"
        else:
            path = "settings.toml"
    return Path(path)


def load_settings(*, path=None, env=None):
    """Load settings from settings file for env.

    See :func:`get_settings_file` for details on settings file
    discovery.

    """
    env_path = get_settings_file(path=path, env=env)
    public_path = env_path.parent / "settings.public.toml"
    toml_settings = []
    for settings_file_path in (public_path, env_path):
        if settings_file_path.is_file():
            with settings_file_path.open() as fp:
                toml_settings.append(toml.load(fp))
    return merge_dicts(*toml_settings)


def getenv(name: str, default=None, required=False) -> Any:
    """Get setting from environment variable or return `default`.

    If the `required` flag is set, the env var MUST be set, even if a
    `default` is provided.

    """
    if required and name not in os.environ:
        raise ImproperlyConfigured(f"Expected environment variable to be set: {name}")
    env_val = os.getenv(name, default)
    if env_val is None:
        return None
    try:
        obj = toml.loads(f"{name} = {env_val}\n")
    except ValueError:
        val = env_val
    else:
        val = obj[name]
    return val
