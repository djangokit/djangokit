"""Django commands and utilities."""
import os
import subprocess
import sys
from getpass import getuser
from pathlib import Path
from typing import List

import typer
from djangokit.core.settings import dotenv_values
from rich.pretty import pretty_repr
from typer import Argument

from .app import app, format_
from .utils import Console, read_project_config
from .utils.run import Args, process_args


@app.command()
def manage(
    args: List[str] = Argument(
        None,
        help="Args passed through to django-admin",
    )
):
    """Run a Django management command"""
    run_django_command(args)


@app.command()
def createsuperuser(username: str = getuser(), email: str = None):
    """Create Django Admin user"""
    if not email:
        email = f"{username}@example.com"
    run_django_command(["createsuperuser", "--username", username, "--email", email])


@app.command()
def migrate():
    """Run all database migrations"""
    run_django_command("migrate")


@app.command()
def start():
    """Run dev server"""
    run_django_command("runserver")


@app.command()
def show_settings(env_only: bool = False, dotenv_path: str = ".env", name: str = None):
    """Show Django settings"""
    console = Console()

    dotenv_settings = dotenv_values(dotenv_path)
    configure_settings_module(dotenv_settings=dotenv_settings)

    if env_only:
        settings = dotenv_settings
    else:
        from django.conf import settings

        settings._setup()
        explicit = settings._explicit_settings
        settings = vars(settings._wrapped)
        settings = {k: v for k, v in settings.items() if k in explicit}

    max_width = min(120, console.width)

    if name:
        if name in settings:
            settings = {name: settings[name]}
            newline = ""
        else:
            console.error(f"Setting does not exist: {name}")
            raise typer.Exit()
    else:
        newline = "\n"

    for name in sorted(settings):
        value = settings[name]
        pretty_value = pretty_repr(value, max_width=sys.maxsize)
        total_width = len(name) + 3 + len(pretty_value)
        if total_width > max_width:
            pretty_value = pretty_repr(value, max_width=max_width)
        console.print(f"{name} = {pretty_value}{newline}", soft_wrap=True)


MODEL_TEMPLATE = """\
from django.db import models


class {class_name}(models.Model):

    class Meta:
        db_table = "{table_name}"
    
    def __str__(self):
        return "{class_name}"
"""


@app.command()
def add_model(
    singular_name: str = Argument(
        ...,
        help='Singular name of model (e.g., project or "user project")',
    )
):
    """Add new Django model"""
    console = Console()

    singular_name = singular_name.lower()
    singular_words = singular_name.split()
    class_name = "".join(word.capitalize() for word in singular_words)
    table_name = "_".join(singular_words)

    package = read_project_config("tool.djangokit.package")
    package_path = Path("src") / package

    models_path = package_path / "models"
    init_path = models_path / "__init__.py"
    model_path = models_path / f"{table_name}.py"

    migration_name = f"add_{table_name}_model"
    migrations_path = package_path / "migrations"
    migration_path = tuple(migrations_path.glob(f"*_{migration_name}.py"))
    migration_path = migration_path[0] if migration_path else None

    admin_path = package_path / "admin.py"

    console.rule(f"Adding model {class_name} to {model_path}")

    if model_path.exists():
        console.error(f"Model exists: {model_path}")
        raise typer.Abort()

    if migration_path and migration_path.exists():
        console.error(f"Migration exists: {migration_path}")
        raise typer.Abort()

    # Add model import to __init__.py ----------------------------------

    with init_path.open("a") as fp:
        fp.write(f"\nfrom . {table_name} import {class_name}\n")

    # Add module for model ---------------------------------------------

    with model_path.open("w") as fp:
        fp.write(MODEL_TEMPLATE.format(class_name=class_name, table_name=table_name))

    # Register model with Django Admin ---------------------------------

    with admin_path.open("a") as fp:
        fp.write(f"\nfrom .models import {class_name}\n")
        fp.write(f"admin.site.register({class_name})")

    # Create migration for model -------------------------------

    run_django_command(f"makemigrations {package} --name {migration_name}", quiet=True)

    format_()

    console.warning("NOTE: Migrations still need to be run")


# Utilities ------------------------------------------------------------


def configure_settings_module(*, dotenv_path=".env", dotenv_settings=None) -> str:
    """Configure Django settings module.

    If the `DJANGO_SETTINGS_MODULE` environment variable isn't present
    or isn't set, this will read `DJANGO_SETTINGS_MODULE` from the
    project's `.env` file and set it as an env var.

    """
    import django

    if os.getenv("DJANGO_SETTINGS_MODULE"):
        settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
    else:
        if dotenv_settings is None:
            dotenv_settings = dotenv_values(dotenv_path)
        settings_module = dotenv_settings["DJANGO_SETTINGS_MODULE"]
        os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

    django.setup()
    return settings_module


def run_django_command(
    args: Args, dotenv_path=".env", quiet=False
) -> subprocess.CompletedProcess:
    """Run a Django management command."""
    console = Console()
    settings_module = configure_settings_module(dotenv_path=dotenv_path)
    if not quiet:
        newline = "\n" if args else ""
        console.print(f'DJANGO_SETTINGS_MODULE = "{settings_module}"{newline}')
    args = ["poetry", "run", "django-admin"] + process_args(args)
    return subprocess.run(args)
