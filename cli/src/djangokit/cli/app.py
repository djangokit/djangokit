"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from typing import Optional

import typer
from djangokit.core.conf import Settings, settings
from djangokit.core.env import load_dotenv
from typer import Context, Option

from .utils import Console, params

app = typer.Typer()


@dataclass
class State:
    """DjangoKit CLI global app state"""

    console: Console = Console(highlight=False)
    cwd: Path = Path.cwd()

    env: str = "development"
    dotenv_file: Path = Path(".env.development")

    settings_module: str = "djangokit.core.settings"
    additional_settings_module: Optional[str] = None
    settings: Settings = field(default_factory=lambda: settings)
    settings_module_configured: bool = False

    use_typescript: bool = True
    quiet: bool = False


state = State()


@app.callback(no_args_is_help=True)
def main(
    ctx: Context,
    env: str = Option(
        state.env,
        "-e",
        "--env",
        envvar="ENV",
    ),
    dotenv_file: Path = Option(
        state.dotenv_file,
        "-f",
        "--dotenv-file",
        envvar="DOTENV_FILE",
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
    use_typescript: bool = Option(
        True,
        "-t",
        "--ts",
        "--typescript",
        help="Use TypeScript (e.g., when generating files)",
        envvar="DJANGOKIT_CLI_USE_TYPESCRIPT",
    ),
    quiet: bool = Option(
        state.quiet,
        "-q",
        "--quiet",
        help="Squelch stdout",
        envvar="DJANGOKIT_CLI_QUIET",
    ),
):
    """DjangoKit CLI

    Commands must be run from the top level directory of your project.

    """
    console = state.console

    if env == "dev":
        env = "development"
    elif env == "prod":
        env = "production"

    environ["ENV"] = env
    environ["DOTENV_FILE"] = str(dotenv_file)
    environ["DJANGO_SETTINGS_MODULE"] = settings_module
    if additional_settings_module:
        environ["DJANGO_ADDITIONAL_SETTINGS_MODULE"] = additional_settings_module

    if not load_dotenv(path=dotenv_file, env=env):
        console.warning(f"No dotenv settings loaded from {dotenv_file}")

    # For CLI settings that weren't specified on the command line or as
    # env vars, see if they were loaded from the .env file.

    def cli_setting(name, value):
        if params.is_default(ctx, name):
            env_name = f"DJANGOKIT_CLI_{name.upper()}"
            if env_name in environ:
                return environ[env_name]
        return value

    use_typescript = cli_setting("use_typescript", use_typescript)
    quiet = cli_setting("quiet", quiet)

    if quiet:
        state.console.quiet = True

    console.header("DjangoKit CLI")
    console.print(f"Environment = {env}")
    console.print(f"Dotenv file = {dotenv_file}")
    console.print(f"Django settings module = {settings_module}")
    console.print(f"Django additional settings module = {additional_settings_module}")
    console.print(f"Use TypeScript = {use_typescript}")
    console.print(f"Quiet = {quiet}")
    console.print()

    state.env = env
    state.dotenv_file = dotenv_file
    state.settings_module = settings_module
    state.additional_settings_module = additional_settings_module
    state.use_typescript = use_typescript
    state.quiet = quiet


@app.command(hidden=True)
def meta():
    """Show the main CLI configuration."""
