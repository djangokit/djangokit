from pathlib import Path
from typing import Optional


def get_standalone_settings_file(cwd: Path, project_root: Optional[Path]) -> Path:
    """Find standalone settings file.

    Search in this order:

    1. `settings.standalone.toml` in CWD
    2. `settings.standalone.toml` in project root directory
    3. `settings.standalone.toml` in `djangokit.cli` package

    """
    file_name = "settings.standalone.toml"

    settings_file = cwd / file_name
    if settings_file.is_file():
        return settings_file

    if project_root is not None:
        settings_file = project_root / file_name
        if settings_file.is_file():
            return settings_file

    default = Path(__file__).parent.parent / file_name
    if not default.is_file():
        raise FileNotFoundError(
            f"Default DjangoKit CLI standalone settings file not found: {default}"
        )
    return default
