from pathlib import Path

import toml


def find_project_root() -> Path | None:
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


def get_project_settings(root: Path) -> dict:
    """Get project CLI settings from pyproject.toml.

    Settings from the `[tool.djangokit.cli]` section will be returned,
    if present.

    """
    if not root.exists():
        raise FileNotFoundError(f"Project root does not exist: {root}")

    if not root.is_dir():
        raise FileNotFoundError(f"Project root is not a directory: {root}")

    project_file = root / "pyproject.toml"

    if not project_file.exists():
        raise FileNotFoundError(
            f"pyproject.toml file not found in project root: {root}"
        )

    with project_file.open() as fp:
        all_settings = toml.load(fp)

    tool_settings = all_settings.get("tool", {})
    djangokit_settings = tool_settings.get("djangokit", {})
    cli_settings = djangokit_settings.get("cli", {})

    return cli_settings
