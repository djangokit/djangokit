from typer import Argument, Option

from .app import app, state
from .django import configure_settings_module

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
  return <h1>{name}</h1>;
}}
"""

API_TEMPLATE = """\
def get(request):
    return {}
"""


@app.command()
def add_route(
    path: str = Argument(..., help="Route path relative to routes directory"),
    name: str = Option(None, help="Route name"),
    with_layout: bool = Option(False, help="Create layout too?"),
    with_api: bool = Option(False, help="Create API module too?"),
    extension: str = Option("tsx", help="Page & layout file name extension"),
):
    """Add a route"""
    configure_settings_module()

    console = state.console
    settings = state.settings
    routes_dir = settings.routes_dir

    route_dir = routes_dir / path
    page_path = route_dir / f"page.{extension}"
    layout_path = route_dir / f"layout.{extension}"
    api_path = route_dir / f"api.py"
    api_init_path = route_dir / f"__init__.py"
    name = name or route_dir.name.title()

    rel_route_dir = route_dir.relative_to(routes_dir.parent)
    rel_page_path = page_path.relative_to(routes_dir.parent)

    console.header(f"Creating route at {rel_route_dir}")

    if not route_dir.exists():
        console.info(f"Creating directory for route: {rel_route_dir}")
        route_dir.mkdir(parents=True)

    if page_path.exists():
        console.warning(f"Overwriting page for route: {rel_page_path}")
    else:
        console.info(f"Creating page for route: {rel_page_path}")
    with page_path.open("w") as fp:
        fp.write(PAGE_TEMPLATE.format(name=name))

    if with_layout:
        rel_layout_path = layout_path.relative_to(routes_dir.parent)
        if layout_path.exists():
            console.warning(f"Overwriting layout for route: {rel_layout_path}")
        else:
            console.info(f"Creating layout for route: {rel_layout_path}")
        with layout_path.open("w") as fp:
            fp.write(LAYOUT_TEMPLATE)

    if with_api:
        rel_api_path = api_path.relative_to(routes_dir.parent)
        rel_api_init_path = api_init_path.relative_to(routes_dir.parent)

        if api_path.exists():
            console.warning(f"Overwriting API module for route: {rel_api_path}")
        else:
            console.info(f"Creating API module for route: {rel_api_path}")
        with api_path.open("w") as fp:
            fp.write(API_TEMPLATE)

        if api_init_path.exists():
            console.warning(
                f"Overwriting API init module for route: {rel_api_init_path}"
            )
        else:
            console.info(f"Creating API init module for route: {rel_api_init_path}")
        api_init_path.touch()

    console.success("Done")
