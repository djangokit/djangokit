from pathlib import Path

import typer
from django.conf import settings
from typer import Argument, Option

from ..app import app, state
from ..utils import exclusive

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

NESTED_LAYOUT_TEMPLATE = """\
import { Outlet } from "react-router-dom";

export default function NestedLayout() {
  return (
    <div>
      <Outlet />
    </div>
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

HANDLERS_TEMPLATE = """\
def get(request):
    return {}
"""


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
    ext = "tsx" if state.use_typescript else "jsx"

    route_dir = routes_dir / path
    page_path = route_dir / f"page.{ext}"
    layout_path = route_dir / f"layout.{ext}"
    nested_layout_path = route_dir / f"nested-layout.{ext}"
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

    if with_layout or with_nested_layout:
        if with_layout:
            path = layout_path
            nested = " "
            template = LAYOUT_TEMPLATE
        else:
            path = nested_layout_path
            nested = " nested "
            template = NESTED_LAYOUT_TEMPLATE
        rel_layout_path = path.relative_to(routes_dir.parent)
        if path.exists():
            console.warning(f"Overwriting{nested}layout {rel_layout_path}")
        else:
            console.info(f"Creating{nested}layout {rel_layout_path}")
        with path.open("w") as fp:
            fp.write(template)

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

    console.header(f"Creating handler module at {rel_route_dir}")

    if not route_dir.exists():
        console.info(f"Creating route directory for handler module: {rel_route_dir}")
        route_dir.mkdir(parents=True)

    if handler_module_path.exists() and not overwrite:
        if not typer.confirm(f"Overwrite handler module {rel_path}?"):
            raise typer.Exit()
        console.warning(f"Overwriting handler module {rel_path}")
    else:
        console.info(f"Creating handler module {rel_path}")

    with handler_module_path.open("w") as fp:
        fp.write(HANDLERS_TEMPLATE)

    if init_path.exists() and not overwrite:
        if not typer.confirm(f"Overwrite handler __init__ module {rel_init_path}?"):
            raise typer.Exit()
        console.warning(f"Overwriting handler __init__ module {rel_init_path}")
    else:
        console.info(f"Creating handler __init__ module {rel_init_path}")

    init_path.touch()
