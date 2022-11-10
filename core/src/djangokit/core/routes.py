from importlib import import_module
from pathlib import Path

from django.urls import path

from .views import AppView


def register_routes(routes_package, view_class=AppView) -> list:
    """Discover & register file-based routes."""
    if isinstance(routes_package, str):
        routes_package = import_module(routes_package)

    urls = []
    routes_path = Path(routes_package.__file__).parent
    page_paths = routes_path.glob("**/*.[jt]sx")

    for rel_page_path in page_paths:
        rel_page_path = rel_page_path.relative_to(routes_path)

        page_name = rel_page_path.parent
        page_name = page_name.as_posix()

        if page_name.startswith("."):
            page_name = page_name[1:]

        pattern = []

        parts = page_name.rsplit("/", 1)
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                name = part[1:-1]
                part = f"<{name}>"
            pattern.append(part)

        pattern = "/".join(pattern)
        url = path(pattern, view_class.as_view())
        urls.append(url)

    return urls
