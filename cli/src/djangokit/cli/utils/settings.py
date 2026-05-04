from pathlib import Path


def get_standalone_settings_file(root: Path) -> Path:
    """Find standalone settings file:

    1. `settings.standalone.toml` in project root directory
    2. `settings.standalone.toml` in `djangokit.cli` package

    """
    file_name = "settings.standalone.toml"

    settings_file = root / file_name
    if settings_file.is_file():
        return settings_file

    default = Path(__file__).parent.parent / file_name
    if not default.is_file():
        raise FileNotFoundError(
            f"Default DjangoKit CLI standalone settings file not found: {default}"
        )
    return default
