from pathlib import Path
from string import Template

import typer
from django.conf import settings
from typer import Argument, Option

from ..app import app
from ..state import state
from ..utils import exclusive

LAYOUT_TEMPLATE = """\
{% extends "app.html" %}

{% block layout %}
    <a href="#main" class="visually-hidden-focusable">Skip to main content</a>

    <header>
        COMMON HEADER CONTENT
    </header>

    <main id="main">
        {% block main %}
            OUTLET FOR MAIN PAGE CONTENT
        {% endblock main %}
    </main>

    <footer>
        COMMON FOOTER CONTENT
    </footer>
{% endblock layout %}
"""

PAGE_TEMPLATE = """\
{% extends "layout.html" %}

{% block main %}
    <div class="p-3">
        PAGE CONTENT (${name})
    </div>
{% endblock %}
"""

NESTED_LAYOUT_TEMPLATE = """\
{% extends "layout.html" %}

{% block main %}
    {% block outlet %}
        OUTLET FOR NESTED LAYOUT CONTENT
    {% endblock outlet %}
{% endblock main %}
"""

NESTED_PAGE_TEMPLATE = """\
{% extends "./layout.html" %}

{% block outlet %}
    NESTED PAGE CONTENT (${name}})
{% endblock outlet%}
"""

HANDLERS_TEMPLATE = """\
from django.shortcuts import get_object_or_404

# from ..models import Model

def get(request):
    return {
        "x": 1,
        "y": 2,
    }
"""


def write_template(template, path, **data):
    template = Template(template)
    content = template.substitute(data)
    with path.open("w") as fp:
        fp.write(content)


@app.command()
def add_page(
    path: Path = Argument(..., help="Route path relative to routes directory"),
    name: str = Option(None, help="Route name"),
    with_layout: bool = Option(
        False,
        help="Create layout too?",
        callback=exclusive("add-page:layout"),
    ),
    with_nested_layout: bool = Option(
        False,
        help="Create nested layout too?",
        callback=exclusive("add-page:layout"),
    ),
    with_handlers: bool = Option(False, help="Create handler module too?"),
    overwrite: bool = Option(False),
):
    """Add a page for a route

    By default, a new page component with *no* layout and *no* handler
    module is created. To create a page with a layout, use the
    `--with-layout` flag. To create a page with an associated handler
    module, use the `--with-handlers` flag.

    """
    console = state.console
    routes_dir = settings.DJANGOKIT.routes_dir

    route_dir = routes_dir / path
    page_path = route_dir / "page.html"
    layout_path = route_dir / "layout.html"
    name = name or route_dir.name.title()

    rel_route_dir = route_dir.relative_to(routes_dir.parent)
    rel_path = page_path.relative_to(routes_dir.parent)

    write_layout = True
    write_page = True

    console.header(f"Creating page at {rel_route_dir}")

    # Create route directory for page
    if not route_dir.exists():
        console.info(f"Creating route directory for page: {rel_route_dir}")
        route_dir.mkdir(parents=True)

    # Create layout for page, if requested
    if with_layout or with_nested_layout:
        if with_layout:
            nested = " "
            layout_template = LAYOUT_TEMPLATE
            page_template = PAGE_TEMPLATE
        else:
            nested = " nested "
            layout_template = NESTED_LAYOUT_TEMPLATE
            page_template = NESTED_PAGE_TEMPLATE

        rel_layout_path = layout_path.relative_to(routes_dir.parent)

        if layout_path.exists():
            if overwrite or typer.confirm(
                f"Overwrite{nested}layout: {rel_layout_path}?"
            ):
                console.warning(f"Overwriting{nested}layout: {rel_layout_path}")
            else:
                write_layout = False
        else:
            console.info(f"Creating{nested}layout: {rel_layout_path}")

        if write_layout:
            write_template(layout_template, layout_path)
    else:
        page_template = PAGE_TEMPLATE

    # Create page
    if page_path.exists():
        if overwrite or typer.confirm(f"Overwrite page {rel_path}?"):
            console.warning(f"Overwriting page: {rel_path}")
        else:
            write_page = False
    else:
        console.info(f"Creating page: {rel_path}")

    if write_page:
        write_template(page_template, page_path, name=name)

    # Create handler module, if requested
    if with_handlers:
        add_handler(path, overwrite)

    console.success("Done")


@app.command()
def add_handler(
    path: Path = Argument(..., help="Route path relative to routes directory"),
    overwrite: bool = Option(False),
):
    """Add a handler module for a route"""
    console = state.console
    routes_dir = settings.DJANGOKIT.routes_dir

    route_dir = routes_dir / path
    handler_module_path = route_dir / "handlers.py"
    init_path = route_dir / "__init__.py"

    rel_route_dir = route_dir.relative_to(routes_dir.parent)
    rel_path = handler_module_path.relative_to(routes_dir.parent)
    rel_init_path = init_path.relative_to(routes_dir.parent)

    write_module = True

    console.header(f"Creating handler module at {rel_route_dir}")

    if not route_dir.exists():
        console.info(f"Creating route directory for handler module: {rel_route_dir}")
        route_dir.mkdir(parents=True)

    if handler_module_path.exists():
        if overwrite or typer.confirm(f"Overwrite handler module: {rel_path}?"):
            console.warning(f"Overwriting handler module: {rel_path}")
        else:
            write_module = False
    else:
        console.info(f"Creating handler module {rel_path}")

    if write_module:
        write_template(HANDLERS_TEMPLATE, handler_module_path)

    if init_path.exists():
        console.warning(f"Handler __init__ module already created: {rel_init_path}")
    else:
        console.info(f"Creating handler __init__ module: {rel_init_path}")
        init_path.touch()
