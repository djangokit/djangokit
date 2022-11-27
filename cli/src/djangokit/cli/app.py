"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
import enum
from dataclasses import dataclass, field
from pathlib import Path

import typer
from djangokit.core.conf import Settings, dotenv_settings, settings
from rich.console import NULL_FILE

from .utils import Console

app = typer.Typer()


class Env(str, enum.Enum):

    dev = "dev"
    development = "development"
    prod = "prod"
    production = "production"


@dataclass
class State:
    """DjangoKit CLI global app state"""

    env: Env = Env.development
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
def main(
    env: Env = Env.development,
    dotenv_path: Path = ".env",
    quiet: bool = typer.Option(state.quiet, help="Squelch stdout"),
):
    """DjangoKit CLI

    Commands must be run from the top level directory of your project.

    """
    if env == Env.dev:
        env = Env.development
    elif env == Env.prod:
        env = Env.production

    if quiet:
        state.console.file = NULL_FILE

    console = state.console
    console.header("DjangoKit CLI")
    console.print(f"environment = {env.value}")
    console.print(f"dotenv file = {dotenv_path}")
    console.print(f"quiet = {quiet}")
    console.print()

    state.env = env
    state.quiet = quiet
    state.dotenv_path = dotenv_path
    state.dotenv_settings = dotenv_settings(dotenv_path)
    state.settings = settings
