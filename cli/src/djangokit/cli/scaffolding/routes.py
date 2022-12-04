import os

import typer
from typer import Argument, Context, Option

from ..app import app, state
from ..django import configure_settings_module
from ..utils import params

LAYOUT_TEMPLATE = """\
import { Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <>
      <header>Header</header>
      <main>
        <Outlet />
      </main>
      <footer>Footer</footer>
    </>
  );
}
"""

PAGE_TEMPLATE = """\
export default function Page() {{
  return (
    <>
      <h2>{name}</h2>
      <div>...</div>
    </>
  );
}}
"""

API_TEMPLATE = """\
def get(request):
    return {}
"""


@app.command()
def add_page(
    path: str = Argument(..., help="Route path relative to routes directory"),
    name: str = Option(None, help="Route name"),
    layout: bool = Option(False, help="Create layout too?"),
    api: bool = Option(False, help="Create API module too?"),
    extension: str = Option(
        "tsx",
        envvar="DJANGOKIT_CLI_PAGE_EXT",
        help="Page & layout file name extension (e.g., tsx or jsx)",
    ),
    overwrite: bool = Option(False),
):
    """Add a page route

    By default, a new page component with *no* layout and *no* API is
    created. To create a page with a layout, use the `--layout` flag. To
    create a page with an API, use the `--api` flag.

    """
    configure_settings_module()

    console = state.console
    settings = state.settings
    routes_dir = settings.routes_dir

    route_dir = routes_dir / path
    page_path = route_dir / f"page.{extension}"
    layout_path = route_dir / f"layout.{extension}"
    name = name or route_dir.name.title()

    rel_route_dir = route_dir.relative_to(routes_dir.parent)
    rel_path = page_path.relative_to(routes_dir.parent)

    console.header(f"Creating page at {rel_route_dir}")

    if not route_dir.exists():
        console.info(f"Creating route directory for page: {rel_route_dir}")
        route_dir.mkdir(parents=True)

    if page_path.exists() and not overwrite:
        if not typer.confirm(f"Overwrite page {rel_path}?"):
            raise typer.Exit()
        console.warning(f"Overwriting page {rel_path}")
    else:
        console.info(f"Creating page {rel_path}")
    with page_path.open("w") as fp:
        fp.write(PAGE_TEMPLATE.format(name=name))

    if layout:
        rel_layout_path = layout_path.relative_to(routes_dir.parent)
        if layout_path.exists():
            console.warning(f"Overwriting layout {rel_layout_path}")
        else:
            console.info(f"Creating layout {rel_layout_path}")
        with layout_path.open("w") as fp:
            fp.write(LAYOUT_TEMPLATE)

    if api:
        add_api(path, overwrite)

    console.success("Done")


@app.command()
def add_api(
    path: str = Argument(..., help="Route path relative to routes directory"),
    overwrite: bool = Option(False),
):
    """Add an API route"""
    configure_settings_module()

    console = state.console
    settings = state.settings
    routes_dir = settings.routes_dir

    route_dir = routes_dir / path
    path = route_dir / "api.py"
    init_path = route_dir / "__init__.py"

    rel_route_dir = route_dir.relative_to(routes_dir.parent)
    rel_path = path.relative_to(routes_dir.parent)
    rel_init_path = init_path.relative_to(routes_dir.parent)

    console.header(f"Creating API module at {rel_route_dir}")

    if not route_dir.exists():
        console.info(f"Creating route directory for API module: {rel_route_dir}")
        route_dir.mkdir(parents=True)

    if path.exists() and not overwrite:
        if not typer.confirm(f"Overwrite API module {rel_path}?"):
            raise typer.Exit()
        console.warning(f"Overwriting API module {rel_path}")
    else:
        console.info(f"Creating API module {rel_path}")

    with path.open("w") as fp:
        fp.write(API_TEMPLATE)

    if init_path.exists() and not overwrite:
        if not typer.confirm(f"Overwrite API __init__ module {rel_init_path}?"):
            raise typer.Exit()
        console.warning(f"Overwriting API __init__ module {rel_init_path}")
    else:
        console.info(f"Creating API __init__ module {rel_init_path}")

    init_path.touch()
