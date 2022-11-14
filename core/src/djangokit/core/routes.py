from importlib import import_module
from pathlib import Path

from django.urls import path

from .views import ApiView, PageView


def register_routes(
    routes_package,
    api_view_class=ApiView,
    page_view_class=PageView,
) -> list:
    """Discover & register file-based routes.

    Finds page-based routes in the specified package and registers a
    Django URL for each.

    Usage in a typical DjangoKit project::

        # src/<package>/urls.py
        from django.urls import include, path
        from djangokit.core import register_routes

        from . import routes

        urlpatterns = [
            path("", include(register_routes(routes))),
        ]

    """
    if isinstance(routes_package, str):
        routes_package = import_module(routes_package)

    urls = []

    routes_path = Path(routes_package.__file__).parent
    page_paths = routes_path.glob("**/*.[jt]sx")
    api_paths = routes_path.glob("**/api.py")

    for page_path in page_paths:
        rel_page_path = page_path.relative_to(routes_path)

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
        url = path(pattern, page_view_class.as_view(page_path=page_path))
        urls.append(url)

    for api_path in api_paths:
        rel_api_path = api_path.relative_to(routes_path)

        api_name = rel_api_path.parent
        api_name = api_name.as_posix()
        api_name = api_name.replace("/", ".")

        if api_name.startswith("."):
            api_name = api_name[1:]

        pattern = []

        parts = api_name.rsplit("/", 1)
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                name = part[1:-1]
                part = f"<{name}>"
            pattern.append(part)

        pattern = "/".join(pattern)
        url = path(f"api/{pattern}", api_view_class.as_view())
        urls.append(url)

    return urls
