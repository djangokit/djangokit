"""Django commands and utilities."""
import os
import subprocess
import sys
from getpass import getuser
from pathlib import Path

import click
import typer
from djangokit.core.conf import dotenv_values
from rich.pretty import pretty_repr
from typer import Argument

from .app import app, state
from .utils.run import Args, process_args, subprocess_run


@click.command(
    add_help_option=False,
    context_settings={"ignore_unknown_options": True},
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def manage(args):
    """Run a Django management command

    This command passes any & all args & options to `django-admin`,
    first configuring things as needed. It implements the functionality
    of `manage.py` in a way that's consistent with the other DjangoKit
    commands.

    """
    run_django_command(args)


@app.command()
def createsuperuser(username: str = getuser(), email: str = None):
    """Create Django Admin user"""
    if not email:
        email = f"{username}@example.com"
    run_django_command(["createsuperuser", "--username", username, "--email", email])


@app.command()
def makemigrations():
    """Create database migrations for project"""
    run_django_command(["makemigrations", state.config.package])


@app.command()
def migrate():
    """Run all database migrations"""
    run_django_command("migrate")


@app.command()
def show_settings(env_only: bool = False, dotenv_path: str = ".env", name: str = None):
    """Show Django settings"""
    console = state.console

    dotenv_settings = dotenv_values(dotenv_path)
    configure_settings_module(dotenv_settings=dotenv_settings)

    if env_only:
        console.header("Django settings loaded from environment variables:")
        settings = dotenv_settings
    else:
        from django.conf import settings

        console.header(f"All Django settings for project (excludes defaults):")

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


@app.command()
def show_urls(dotenv_path: str = ".env", include_admin: bool = False):
    """Show Django URL patterns in order of precedence

    Django Admin URLs are excluded by default.

    """
    from django.urls import get_resolver, URLResolver, URLPattern

    def get_patterns(obj, ancestors=()):
        patterns = []
        if isinstance(obj, list):
            for item in obj:
                patterns.extend(get_patterns(item, ancestors))
        elif isinstance(obj, URLResolver):
            ancestors += (obj.pattern,)
            for item in obj.url_patterns:
                patterns.extend(get_patterns(item, ancestors))
        elif isinstance(obj, URLPattern):
            prefix = "".join(str(segment) for segment in ancestors)
            patterns.append(f"{prefix}{obj.pattern}")
        else:
            raise TypeError(f"Unexpected object of type {type(obj)}: {obj}")
        return patterns

    console = state.console
    configure_settings_module(dotenv_path=dotenv_path)

    resolver = get_resolver()
    url_patterns = get_patterns(resolver)

    if not include_admin:
        url_patterns = (p for p in url_patterns if not p.startswith("^/$admin"))

    console.header("Django URL patterns in order of precedence:")
    for pattern in url_patterns:
        console.info(pattern)


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
    console = state.console

    singular_name = singular_name.lower()
    singular_words = singular_name.split()
    class_name = "".join(word.capitalize() for word in singular_words)
    table_name = "_".join(singular_words)

    package = state.config.package
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
    console = state.console
    settings_module = configure_settings_module(dotenv_path=dotenv_path)
    if not quiet:
        newline = "\n" if args else ""
        console.print(f'DJANGO_SETTINGS_MODULE = "{settings_module}"{newline}')
    args = ["poetry", "run", "django-admin"] + process_args(args)
    return subprocess_run(args)
