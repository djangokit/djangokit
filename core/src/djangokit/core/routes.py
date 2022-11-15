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
    routes_package = routes_package.__package__

    page_paths = routes_path.glob("**/*.[jt]sx")
    api_paths = routes_path.glob("**/api.py")

    for page_path in page_paths:
        rel_page_path = page_path.relative_to(routes_path)

        page_name = rel_page_path.parent
        page_name = page_name.as_posix()

        if page_name.startswith("."):
            page_name = page_name[1:]

        segments = []

        parts = page_name.rsplit("/", 1)
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                name = part[1:-1]
                part = f"<{name}>"
            segments.append(part)

        pattern = "/".join(segments)
        view = page_view_class.as_view(page_path=page_path)
        urls.append(path(pattern, view))

    for api_path in api_paths:
        rel_api_path = api_path.relative_to(routes_path)

        api_name = rel_api_path.parent
        api_name = api_name.as_posix()
        api_name = api_name.replace("/", ".")
        api_name = api_name[1:] if api_name.startswith(".") else api_name

        if api_name:
            api_module_name = f"{routes_package}.{api_name}.api"
        else:
            api_module_name = f"{routes_package}.api"

        api_module = import_module(api_module_name)

        segments = []

        parts = api_name.rsplit(".", 1)
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                name = part[1:-1]
                part = f"<{name}>"
            segments.append(part)

        pattern = "/".join(segments)
        pattern = f"api/{pattern}"
        view = api_view_class.as_view(api_module=api_module)
        urls.append(path(pattern, view))

    return urls
