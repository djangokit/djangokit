from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .utils import Console


@dataclass
class State:
    """DjangoKit CLI global app state"""

    env: str = "development"

    cwd: Path = Path()
    project_root: Optional[Path] = None

    settings_module: str = "djangokit.core.settings"
    additional_settings_module: Optional[str] = None
    settings_file: Path = Path("settings.development.toml")

    use_typescript: bool = True
    quiet: bool = False

    console: Console = Console(highlight=False)


state = State()
