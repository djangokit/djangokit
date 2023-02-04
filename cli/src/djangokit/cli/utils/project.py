from pathlib import Path
from typing import Optional

import toml


def find_project_root() -> Optional[Path]:
    """Find project root directory.

    The root directory is indicated solely by the presence of a
    `pyproject.toml` file.

    """
    current = Path.cwd()
    fs_root = Path(current.root)
    n = 0
    while n < 512:
        n += 1
        if (current / "pyproject.toml").is_file():
            return current
        if current == fs_root:
            break
        current = current.parent
    return None


def get_project_settings() -> dict:
    """Get project CLI settings from pyproject.toml.

    Settings from the `[tool.djangokit.cli]` section will be returned,
    if present.

    """
    root = find_project_root()

    if root is None:
        return {}

    project_file = root / "pyproject.toml"

    if not project_file.is_file():
        return {}

    with project_file.open() as fp:
        all_settings = toml.load(fp)

    tool_settings = all_settings.get("tool", {})
    djangokit_settings = tool_settings.get("djangokit", {})
    cli_settings = djangokit_settings.get("cli", {})

    return cli_settings
