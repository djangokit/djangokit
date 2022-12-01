"""Django commands and utilities."""
import json
import os
import subprocess
import sys
from getpass import getuser
from fnmatch import fnmatch
from typing import List

import click
import typer
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
    configure_settings_module()
    run_django_command(["makemigrations", state.settings.app_label])


@app.command()
def migrate():
    """Run all database migrations"""
    run_django_command("migrate")


@app.command()
def show_settings(
    dotenv: bool = False,
    only: str = typer.Option(
        None,
        help=(
            "Show only the specified setting or settings matching a "
            "pattern. Patterns use fnmatch syntax. As a special case, "
            "`PREFIX_` is equivalent to `PREFIX_*`."
        ),
    ),
):
    """Show Django settings"""
    console = state.console
    configure_settings_module()

    if dotenv:
        settings = state.dotenv_settings
    else:
        from django.conf import settings

        settings._setup()
        explicit = settings._explicit_settings
        settings = vars(settings._wrapped)
        settings = {k: v for k, v in settings.items() if k in explicit}

    max_width = min(120, console.width)

    if only:
        console.header(f"Showing the specified setting only:")
        if only in settings:
            matching_settings = {only: settings[only]}
        else:
            matching_settings = {}
            for name, val in settings.items():
                if fnmatch(name, only):
                    matching_settings[name] = val
            if not matching_settings and only.endswith("_"):
                pattern = f"{only}*"
                for name, val in settings.items():
                    if fnmatch(name, pattern):
                        matching_settings[name] = val
        if matching_settings:
            settings = matching_settings
            newline = "\n" if len(settings) > 1 else ""
        else:
            console.error(f"Could not find matching setting(s): {only}")
            raise typer.Abort()
    elif dotenv:
        console.header("Settings loaded from .env file(s):")
        newline = "\n"
    else:
        console.header(f"All Django settings for project (excludes defaults):")
        newline = "\n"

    for name in sorted(settings):
        value = settings[name]
        pretty_value = pretty_repr(value, max_width=sys.maxsize)
        total_width = len(name) + 3 + len(pretty_value)
        if total_width > max_width:
            pretty_value = pretty_repr(value, max_width=max_width)
        console.print(
            f"{name} = {pretty_value}{newline}", soft_wrap=True, highlight=True
        )


@app.command()
def show_urls(include_admin: bool = False):
    """Show Django URL patterns in order of precedence

    Django Admin URLs are excluded by default.

    """
    from django.urls import URLPattern, URLResolver, get_resolver

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
    configure_settings_module()

    resolver = get_resolver()
    url_patterns = get_patterns(resolver)

    if not include_admin:
        url_patterns = (p for p in url_patterns if not p.startswith("^/$admin"))

    console.header("Django URL patterns in order of precedence:")
    for pattern in url_patterns:
        console.print(pattern)


@app.command()
def add_model(
    singular_name: str = Argument(
        ...,
        help='Singular name of model (e.g., post or "user post")',
    ),
    fields: List[str] = Argument(
        None,
        help="Fields to add to the model (e.g., title:str)",
    ),
    register_admin: bool = True,
):
    """Add new Django model"""
    from django.template import Context, Template

    configure_settings_module()

    console = state.console
    settings = state.settings

    # Add model --------------------------------------------------------

    singular_name = singular_name.lower()
    singular_words = singular_name.split()
    class_name = "".join(word.capitalize() for word in singular_words)
    table_name = "_".join(singular_words)

    models_dir = settings.models_dir
    init_path = models_dir / "__init__.py"
    model_path = models_dir / f"{table_name}.py"

    console.header(f"Adding model {class_name} to {model_path}")

    if model_path.exists():
        console.error(f"Model {class_name} exists at {model_path}")
        raise typer.Abort()

    model_fields = {}
    for field in fields:
        name, *type_ = field.split(":", 1)
        if type_:
            type_ = type_[0]
        elif name in ("created", "created_at"):
            type_ = "created"
        elif name in ("updated", "updated_at"):
            type_ = "updated"
        else:
            console.error(f"Field `{name}` requires a type; e.g. {name}:str")
            raise typer.Abort()
        model_fields[name] = get_model_field(type_)

    template = Template(MODEL_TEMPLATE)
    context = Context(
        {
            "class_name": class_name,
            "table_name": table_name,
            "fields": model_fields,
        }
    )
    contents = template.render(context)

    with model_path.open("w") as fp:
        fp.write(contents)

    # Add model import to __init__.py ----------------------------------

    with init_path.open("a") as fp:
        fp.write(f"\nfrom . {table_name} import {class_name}\n")

    # Register model with Django Admin ---------------------------------

    if register_admin:
        admin_path = settings.app_dir / "admin.py"
        with admin_path.open("a") as fp:
            fp.write(f"\nfrom .models import {class_name}\n")
            fp.write(f"admin.site.register({class_name})")

    console.success(f"Model {class_name} created at {model_path}")
    console.warning(
        "\nTODO:\n"
        "\n1. Check model definition"
        "\n2. Make migration with `dk makemigrations`"
        "\n3. Run migrations with `dk migrate`"
    )


MODEL_TEMPLATE = """\
from django.db import models


class {{ class_name }}(models.Model):

    class Meta:
        db_table = "{{ table_name }}"
    {% for name, value in fields.items %}
    {{ name }} = {{ value }}{% endfor %}

    def __str__(self):
        return "{{ class_name }}"
"""


def get_model_field(type_: str) -> str:
    if type_ in ("str", "string"):
        return "models.CharField(max_length=255)"
    if type_ == "text":
        return "models.TextField()"
    if type_ in ("bool", "boolean"):
        return "models.BooleanField()"
    if type_ in ("int", "integer"):
        return "models.IntegerField()"
    if type_ == "date":
        return "models.DateField()"
    if type_ == "time":
        return "models.TimeField()"
    if type_ == "datetime":
        return "models.DateTimeField()"
    if type_ == "created":
        return "models.DateTimeField(auto_now_add=True)"
    if type_ == "updated":
        return "models.DateTimeField(auto_now=True)"
    return type_


# Utilities ------------------------------------------------------------


def configure_settings_module(**env_vars):
    """Configure Django settings module.

    Settings module discovery if the `DJANGO_SETTINGS_MODULE`
    environment variable isn't already set:

    1. If `DJANGO_SETTINGS_MODULE` is present in the project's .env
       file, the `DJANGO_SETTINGS_MODULE` env var is set to that value.
    2. Otherwise, the `DJANGO_SETTINGS_MODULE` env var is set to the
       default value: "djangokit.core.settings".

    After `DJANGO_SETTINGS_MODULE` is set, `django.setup()` is called
    and the name of the settings module is returned.

    """
    if state.settings_module_configured:
        return

    import django

    os.environ["DJANGO_SETTINGS_MODULE"] = state.settings_module

    if state.additional_settings_module:
        module = state.additional_settings_module
        os.environ["DJANGO_ADDITIONAL_SETTINGS_MODULE"] = module

    for name, val in env_vars.items():
        if isinstance(val, str):
            env_val = val
        else:
            try:
                env_val = json.dumps(val)
            except ValueError:
                env_val = str(val)
        os.environ[name] = env_val

    django.setup()
    state.settings_module_configured = True


def run_django_command(args: Args) -> subprocess.CompletedProcess:
    """Run a Django management command."""
    configure_settings_module()
    args = ["django-admin"] + process_args(args)
    return subprocess_run(args)
