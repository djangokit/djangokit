"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
import dataclasses
import os
import sys
from os import environ
from pathlib import Path

import django
import typer
from djangokit.core.conf import load_settings
from rich.table import Table
from typer import Context, Option

from . import __version__
from .state import state
from .utils import get_project_settings, find_project_root, get_standalone_settings_file, params

app = typer.Typer()


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
    standalone: bool = Option(
        False,
        "-s",
        "--standalone",
        help="Force standalone mode",
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

    CWD will be changed to the project root before running subcommands.

    """
    console = state.console

    if env == "dev":
        env = "development"
    elif env == "prod":
        env = "production"

    cwd = Path.cwd()
    project_root = find_project_root()
    project_settings = get_project_settings()

    if project_root:
        os.chdir(project_root)

    # If standalone mode wasn't explicitly requested, determine whether
    # standalone mode should be used.
    if params.is_default(ctx, "standalone") and not standalone:
        if project_settings.get("standalone", False):
            standalone = True
        elif project_root is None:
            console.warning("Project root not found; running in standalone mode")
            standalone = True
        elif (cwd / "settings.standalone.toml").is_file():
            console.warning("Found standalone settings file in CWD; running in standalone mode")
            standalone = True

    if params.is_default(ctx, "settings_file"):
        if standalone:
            settings_file = get_standalone_settings_file(cwd, project_root)
        else:
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

    state.env = env
    state.cwd = cwd
    state.project_root = project_root
    state.settings_module = settings_module
    state.additional_settings_module = additional_settings_module
    state.settings_file = settings_file
    state.use_typescript = use_typescript
    state.quiet = quiet

    console.header(f"DjangoKit CLI version {__version__}")
    state_table = Table()
    state_table.add_column("name")
    state_table.add_column("value")
    for field in dataclasses.fields(state):
        name = field.name
        if name == "console":
            continue
        val = str(getattr(state, name))
        state_table.add_row(name, val)
    console.print(state_table)
    console.print()

    if state.project_root is not None:
        path = str(state.project_root / "src")
        if path not in sys.path:
            sys.path.insert(0, path)

    django.setup()


@app.command()
def info():
    """Show the main CLI configuration"""
