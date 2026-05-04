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
from rich.table import Table
from typer import Context, Exit, Option

from . import __version__
from .state import state
from .utils import get_standalone_settings_file, params

app = typer.Typer(
    context_settings={
        "help_option_names": ["-h", "--help"],
    }
)


@app.callback(no_args_is_help=True)
def main(
    ctx: Context,
    env: str = Option(
        state.env,
        "-e",
        "--env",
        envvar="ENV",
    ),
    project_root: Path | None = Option(
        None,
        "-p",
        "--project-root",
        help="Project root",
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

    try:
        project_root = state.set_project_root(project_root)
    except FileNotFoundError as exc:
        console.err_console.error(exc)
        raise Exit(1) from None

    if not params.is_default(ctx, "project_root"):
        try:
            i = sys.argv.index("-p", 1)
        except ValueError:
            i = sys.argv.index("--project-root", 1)
        sys.argv[i + 1] = str(project_root)

    if params.is_default(ctx, "settings_file"):
        if env == "standalone":
            try:
                settings_file = get_standalone_settings_file(project_root)
            except FileNotFoundError as exc:
                console.error(exc)
                raise Exit(1) from None
        else:
            settings_file = project_root / f"settings.{env}.toml"

    settings_file = settings_file.resolve()

    state.env = env
    state.settings_module = settings_module
    state.additional_settings_module = additional_settings_module
    state.settings_file = settings_file
    state.quiet = quiet
    state.console.quiet = quiet

    environ["ENV"] = env
    environ["DJANGO_SETTINGS_MODULE"] = settings_module
    if additional_settings_module:
        environ["DJANGO_ADDITIONAL_SETTINGS_MODULE"] = additional_settings_module
    environ["DJANGO_SETTINGS_FILE"] = str(settings_file)

    # Always show DjangoKit CLI info before running command

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

    os.chdir(state.project_root)
    django.setup()


@app.command()
def info():
    """Show the main CLI configuration"""
    state.console.print(f"CWD: {Path.cwd()}")
