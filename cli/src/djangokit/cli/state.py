from dataclasses import dataclass, field
from pathlib import Path

from .utils import Console, find_project_root, get_project_settings


def default_factory_env():
    files = Path.cwd().glob("settings.*.toml")
    envs = sorted(file.stem.split(".", 1)[1] for file in files)
    if len(envs) == 0:
        return "standalone"
    if "development" in envs:
        return "development"
    if "production" in envs:
        return "production"
    return envs[0]


def default_factory_settings_file():
    env = default_factory_env()
    return f"settings.{env}.toml"


@dataclass
class State:
    """DjangoKit CLI global app state"""

    project_root: Path = Path.cwd()

    env: str = field(default_factory=default_factory_env)
    settings_module: str = "djangokit.core.settings"
    additional_settings_module: str | None = None
    settings_file: Path = field(default_factory=default_factory_settings_file)
    quiet: bool = False

    console: Console = Console(highlight=False)

    def set_project_root(self, root: Path | None):
        """"""
        if root:
            self.project_root = root.resolve()
        else:
            found_root = find_project_root()
            if found_root:
                self.project_root = found_root
            else:
                # Use default CWD
                return self.project_root

        settings = get_project_settings(self.project_root)

        if "project_root" in settings:
            raise ValueError(f"Project root cannot be set via settings in {root}")

        state = State(**settings)

        self.env = state.env
        self.settings_module = state.settings_module
        self.additional_settings_module = state.additional_settings_module
        self.settings_file = state.settings_file
        self.quiet = state.quiet
        self.console.quiet = state.quiet

        return self.project_root


state = State()
