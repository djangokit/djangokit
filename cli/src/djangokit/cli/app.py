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
from typer import Context, Option

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
    settings_module: str = "djangokit.core.settings"
    additional_settings_module: str = None
    settings_module_configured: bool = False


state = State()


@app.callback(no_args_is_help=True)
def main(
    ctx: Context,
    env: Env = Option(
        state.env,
        "-e",
        "--env",
    ),
    dotenv_path: Path = Option(
        state.dotenv_path,
        "-t",
        "--dotenv",
    ),
    settings_module: str = Option(
        state.settings_module,
        "-m",
        "--settings-module",
        envvar="DJANGO_SETTINGS_MODULE",
    ),
    additional_settings_module: str = Option(
        state.additional_settings_module,
        "-a",
        "--additional-settings-module",
        envvar="DJANGO_ADDITIONAL_SETTINGS_MODULE",
    ),
    quiet: bool = Option(
        state.quiet,
        "-q",
        "--quiet",
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
    source = ctx.get_parameter_source("settings_module")
    if source == ParameterSource.DEFAULT:
        if "DJANGO_SETTINGS_MODULE" in dotenv_settings:
            settings_module = dotenv_settings["DJANGO_SETTINGS_MODULE"]

    source = ctx.get_parameter_source("additional_settings_module")
    if source == ParameterSource.DEFAULT:
        if "DJANGO_ADDITIONAL_SETTINGS_MODULE" in dotenv_settings:
            module = dotenv_settings["DJANGO_ADDITIONAL_SETTINGS_MODULE"]
            additional_settings_module = module

    console = state.console
    console.header("DjangoKit CLI")
    console.print(f"Environment = {env.value}")
    console.print(f"Dotenv file = {dotenv_path}")
    console.print(f"Django settings module = {settings_module}")
    console.print(f"Django additional settings module = {additional_settings_module}")
    console.print(f"Quiet = {quiet}")
    console.print()

    state.env = env
    state.dotenv_path = dotenv_path
    state.dotenv_settings = dotenv_settings
    state.settings_module = settings_module
    state.additional_settings_module = additional_settings_module
    state.quiet = quiet
