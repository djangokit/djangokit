"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
from dataclasses import dataclass
from os import environ
from pathlib import Path
from typing import Optional

import django
import typer
from djangokit.core.conf import load_settings
from typer import Context, Option

from .utils import Console, params

app = typer.Typer()


@dataclass
class State:
    """DjangoKit CLI global app state"""

    console: Console = Console(highlight=False)
    cwd: Path = Path.cwd()

    env: str = "development"

    settings_module: str = "djangokit.core.settings"
    additional_settings_module: Optional[str] = None
    settings_file: Path = Path("settings.development.toml")

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
    settings_file: Path = Option(
        state.settings_file,
        "-f",
        "--settings-file",
        envvar="DJANGO_SETTINGS_FILE",
    ),
    use_typescript: bool = Option(
        True,
        "-t",
        "--ts",
        "--typescript",
        help="Use TypeScript (e.g., when generating files)",
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

    if env == "dev":
        env = "development"
    elif env == "prod":
        env = "production"

    if params.is_default(ctx, "settings_file"):
        settings_file = Path(f"settings.{env}.toml")

    settings_file = settings_file.absolute()
    loaded_settings = load_settings(path=settings_file, env=env)
    dk_settings = loaded_settings.get("djangokit", {"cli": {}})
    cli_settings = dk_settings.get("cli", {})

    # For CLI settings that weren't specified on the command line or as
    # env vars, see if they were loaded from the settings file.

    def cli_setting(name, value):
        if params.is_default(ctx, name):
            if name in cli_settings:
                return cli_settings[name]
        return value

    settings_module = cli_setting("settings_module", settings_module)
    additional_settings_module = cli_setting(
        "additional_settings_module", additional_settings_module
    )
    use_typescript = cli_setting("use_typescript", use_typescript)
    quiet = cli_setting("quiet", quiet)

    environ["ENV"] = env
    environ["DJANGO_SETTINGS_MODULE"] = settings_module
    if additional_settings_module:
        environ["DJANGO_ADDITIONAL_SETTINGS_MODULE"] = additional_settings_module
    environ["DJANGO_SETTINGS_FILE"] = str(settings_file)

    if quiet:
        state.console.quiet = True

    console.header("DjangoKit CLI")
    console.print(f"Environment = {env}")
    console.print(f"Django settings module = {settings_module}")
    console.print(f"Django additional settings module = {additional_settings_module}")
    console.print(f"Settings file = {settings_file}")
    console.print(f"Use TypeScript = {use_typescript}")
    console.print(f"Quiet = {quiet}")
    console.print()

    state.env = env
    state.settings_module = settings_module
    state.additional_settings_module = additional_settings_module
    state.settings_file = settings_file
    state.use_typescript = use_typescript
    state.quiet = quiet

    django.setup()


@app.command(hidden=True)
def meta():
    """Show the main CLI configuration."""
