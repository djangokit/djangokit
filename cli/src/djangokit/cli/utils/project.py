import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml


@dataclass
class Config:
    """Config that can be specified in pyproject.toml"""

    package: str = None
    has_python: bool = True
    has_js: bool = True


def read_project_config(default=None) -> Config:
    """Read project config from pyproject.toml."""
    path = Path("pyproject.toml")
    with path.open("rb") as fp:
        data = toml.load(fp)
    key = "tool.djangokit"
    segments = key.split(".")
    for segment in segments:
        if segment in data:
            data = data[segment]
        else:
            return default
    config = Config(**data)
    return config
