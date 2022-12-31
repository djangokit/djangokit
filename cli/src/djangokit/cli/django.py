"""Django commands and utilities."""
import sys
from fnmatch import fnmatch
from getpass import getuser
from typing import List, Optional

import click
from django.conf import settings
from django.core.management import execute_from_command_line
from django.template import Context, Template
from django.urls import URLPattern, URLResolver, get_resolver
from rich.pretty import pretty_repr
from typer import Abort, Argument, Option

from .app import app, state
from .utils.run import Args, process_args


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
def createsuperuser(username: str = getuser(), email: Optional[str] = None):
    """Create Django Admin user"""
    if not email:
        email = f"{username}@example.com"
    run_django_command(["createsuperuser", "--username", username, "--email", email])


@app.command()
def makemigrations():
    """Create database migrations for project"""
    run_django_command(["makemigrations", settings.DJANGOKIT.app_label])


@app.command()
def migrate():
    """Run all database migrations"""
    run_django_command("migrate")


@app.command()
def shell():
    """Run shell"""
    run_django_command("shell")


@app.command()
def dbshell():
    """Run database shell"""
    run_django_command("dbshell")


@app.command()
def collectstatic(static_root: Optional[str] = None, clear: bool = False):
    """Collect static files."""
    if static_root is not None:
        settings.STATIC_ROOT = static_root
    run_django_command(["collectstatic", "--clear" if clear else ""])


@app.command()
def show_settings(
    all_: bool = Option(False, "--all", help="Show all settings"),
    only: str = Option(
        None,
        help=(
            "Show only the specified setting or settings matching a "
            "pattern. Patterns use fnmatch syntax. As a special case, "
            "`PREFIX_` is equivalent to `PREFIX_*`. (`Implies --all`)."
        ),
    ),
):
    """Show Django settings

    By default, only DjangoKit settings are shown, including the default
    Django settings used by Django apps.

    """
    console = state.console
    explicit_settings = settings._explicit_settings
    settings_to_show = vars(settings._wrapped)
    max_width = min(120, console.width)

    if all_ or only:
        settings_to_show = settings_to_show.copy()
        del settings_to_show["_explicit_settings"]
    else:
        settings_to_show = {
            k: v for k, v in settings_to_show.items() if k in explicit_settings
        }

    if only:
        header = "Showing the specified setting only:"
        if only in settings_to_show:
            matching_settings = {only: settings_to_show[only]}
        else:
            matching_settings = {}
            for name, val in settings_to_show.items():
                if fnmatch(name, only):
                    matching_settings[name] = val
            if not matching_settings and only.endswith("_"):
                pattern = f"{only}*"
                for name, val in settings_to_show.items():
                    if fnmatch(name, pattern):
                        matching_settings[name] = val
        if matching_settings:
            settings_to_show = matching_settings
        else:
            console.error(f"Could not find matching setting(s): {only}")
            raise Abort()
    elif all_:
        header = "ALL Django settings for project:"
    else:
        header = "Django settings for project (excludes defaults):"

    console.header(header)
    console.warning("Settings changed from defaults are prefixed with a bang!\n")
    newline = "\n" if len(settings_to_show) > 1 else ""

    for name in sorted(settings_to_show):
        value = settings_to_show[name]
        pretty_value = pretty_repr(value, max_width=sys.maxsize)
        total_width = len(name) + 3 + len(pretty_value)
        if total_width > max_width:
            pretty_value = pretty_repr(value, max_width=max_width)
        if name in explicit_settings:
            name = f"![yellow]{name}[/yellow]"
        console.print(
            f"{name} = {pretty_value}{newline}", soft_wrap=True, highlight=True
        )


@app.command()
def show_urls(include_admin: bool = False):
    """Show Django URL patterns in order of precedence

    Django Admin URLs are excluded by default.

    """

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
    resolver = get_resolver()
    url_patterns = get_patterns(resolver)
    prefix = rf"^/{settings.DJANGOKIT.admin_prefix}"

    if not include_admin:
        url_patterns = (p for p in url_patterns if not p.startswith(prefix))

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
    console = state.console

    # Add model --------------------------------------------------------

    singular_name = singular_name.lower()
    singular_words = singular_name.split()
    class_name = "".join(word.capitalize() for word in singular_words)
    table_name = "_".join(singular_words)

    models_dir = settings.DJANGOKIT.models_dir
    init_path = models_dir / "__init__.py"
    model_path = models_dir / f"{table_name}.py"

    console.header(f"Adding model {class_name} to {model_path}")

    if model_path.exists():
        console.error(f"Model {class_name} exists at {model_path}")
        raise Abort()

    model_fields = {}
    for field in fields:
        name, *rest = field.split(":", 1)
        if rest:
            type_ = rest[0]
        elif name in ("created", "created_at"):
            type_ = "created"
        elif name in ("updated", "updated_at"):
            type_ = "updated"
        else:
            console.error(f"Field `{name}` requires a type; e.g. {name}:str")
            raise Abort()
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
        admin_path = settings.DJANGOKIT.package_dir / "admin.py"
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


def run_django_command(args: Args):
    """Run a Django management command."""
    args = ["django-admin"] + process_args(args)
    state.console.command(">", " ".join(args))
    execute_from_command_line(args)
