"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
import enum
import os
from dataclasses import dataclass, field
from pathlib import Path

import typer
from djangokit.core.conf import Settings, settings
from djangokit.core.env import dotenv_settings as get_dotenv_settings
from typer import Context, Option

from .utils import Console, params

app = typer.Typer()


class Env(enum.Enum):

    dev = "dev"
    development = "development"
    prod = "prod"
    production = "production"


@dataclass
class State:
    """DjangoKit CLI global app state"""

    env: Env = Env.development
    quiet: bool = False
    dotenv_path: Path = Path(".env.development")
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
        state.env.value,
        "-e",
        "--env",
        envvar="ENV",
    ),
    dotenv_path: Path = Option(
        state.dotenv_path,
        "-t",
        "--dotenv",
        envvar="DOTENV_PATH",
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
    console = state.console

    if env == Env.dev:
        env = Env.development
    elif env == Env.prod:
        env = Env.production

    env = env.value

    # Set .env path from env when .env path isn't passed in or set as an
    # env var.
    if params.is_default(ctx, "dotenv_path"):
        dotenv_path = f".env.{env}"

    os.environ["DOTENV_PATH"] = str(dotenv_path)

    dotenv_settings = get_dotenv_settings(dotenv_path)

    if not dotenv_settings:
        console.warning(f"No dotenv settings loaded from {dotenv_path}")

    # Set Django settings module from .env when it's not passed in or
    # set as an env var.
    key = "DJANGO_SETTINGS_MODULE"
    if params.is_default(ctx, "settings_module") and key in dotenv_settings:
        settings_module = dotenv_settings[key]
    key = "DJANGO_ADDITIONAL_SETTINGS_MODULE"
    if params.is_default(ctx, "additional_settings_module") and key in dotenv_settings:
        settings_module = dotenv_settings[key]

    if quiet:
        state.console.quiet = True

    console.header("DjangoKit CLI")
    console.print(f"Environment = {env}")
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


@app.command(hidden=True)
def meta():
    """Show the main CLI configuration."""
