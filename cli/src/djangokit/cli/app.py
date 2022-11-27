"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
from dataclasses import dataclass, field
from pathlib import Path

import typer
from djangokit.core.conf import Settings, dotenv_settings, settings

from .utils import Console

app = typer.Typer()


@dataclass
class State:
    """DjangoKit CLI global app state"""

    env: str = "dev"
    quiet: bool = False
    dotenv_path: Path = Path(".env")
    dotenv_settings: dict = field(default_factory=dict)
    settings: Settings = None
    console: Console = Console(highlight=False)
    cwd: Path = Path.cwd()
    has_node_modules: bool = (Path.cwd() / "node_modules").exists()
    django_settings_module: str = None


state = State()


@app.callback(no_args_is_help=True)
def main(env: str = state.env, quiet: bool = state.quiet, dotenv_path: Path = ".env"):
    """DjangoKit CLI

    Commands must be run from the top level directory of your project.

    """
    state.env = env
    state.quiet = quiet
    state.dotenv_path = dotenv_path
    state.dotenv_settings = dotenv_settings(dotenv_path)
    state.settings = settings
