from pathlib import Path
from typing import Optional


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
