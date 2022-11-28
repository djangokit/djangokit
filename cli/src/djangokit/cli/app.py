"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
import enum
from dataclasses import dataclass, field
from pathlib import Path

import typer
from click.core import ParameterSource
from djangokit.core.conf import Settings, settings
from djangokit.core.env import dotenv_settings as get_dotenv_settings
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
    settings: Settings = field(default_factory=lambda: settings)
    console: Console = Console(highlight=False)
    cwd: Path = Path.cwd()
    has_node_modules: bool = (Path.cwd() / "node_modules").exists()
    django_settings_module: str = "djangokit.core.settings"
    django_settings_module_configured: bool = False


state = State()


@app.callback(no_args_is_help=True)
def main(
    ctx: typer.Context,
    env: Env = state.env,
    dotenv_path: Path = state.dotenv_path,
    django_settings_module: str = typer.Option(
        state.django_settings_module,
        envvar="DJANGO_SETTINGS_MODULE",
    ),
    quiet: bool = typer.Option(
        state.quiet,
        help="Squelch stdout",
    ),
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

    dotenv_settings = get_dotenv_settings(dotenv_path)

    # When the Django settings module isn't specified on the command
    # line and also isn't present as an env var, see if it's present in
    # the project's .env settings; otherwise, use the default.
    if ctx.get_parameter_source("django_settings_module") == ParameterSource.DEFAULT:
        if "DJANGO_SETTINGS_MODULE" in dotenv_settings:
            django_settings_module = dotenv_settings["DJANGO_SETTINGS_MODULE"]

    console = state.console
    console.header("DjangoKit CLI")
    console.print(f"Environment = {env.value}")
    console.print(f"Dotenv file = {dotenv_path}")
    console.print(f"Django settings module = {django_settings_module}")
    console.print(f"Quiet = {quiet}")
    console.print()

    state.env = env
    state.dotenv_path = dotenv_path
    state.dotenv_settings = dotenv_settings
    state.django_settings_module = django_settings_module
    state.quiet = quiet
