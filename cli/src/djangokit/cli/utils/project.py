import sys
from pathlib import Path

if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml


def read_project_config(key=None):
    """Read project config from pyproject.toml."""
    path = Path("pyproject.toml")
    with path.open("rb") as fp:
        data = toml.load(fp)
    if key:
        parts = key.split(".")
        part = parts[0]
        obj = data[part]
        for part in parts[1:]:
            obj = obj[part]
        return obj
    return data
