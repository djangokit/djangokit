from pathlib import Path

from django.apps import apps
from django.urls import include, path

from .conf import get_setting
from .utils import find_apis, find_pages
from .views import ApiView, PageView


def create_routes(
    prefix="",
    page_view_class=PageView,
    api_view_class=ApiView,
) -> list:
    """Discover & register file-based routes.

    Finds page-based & API routes in the specified package and registers
    a Django URL for each.

    Usage in a typical DjangoKit project::

        # src/<package>/urls.py
        from django.contrib import admin
        from django.urls import include, path
        from djangokit.core import create_routes

        from . import routes

        urlpatterns = [
            path("admin/", admin.site.urls),
            create_routes(routes),
        ]

    """
    package = get_setting("package")
    routes_package = f"{package}.routes"
    app = apps.get_app_config(package)
    app_dir = Path(app.path)
    routes_dir = app_dir / "routes"
    page_info = find_pages(routes_dir)
    api_info = find_apis(routes_dir, routes_package)
    urls = []

    for info in api_info:
        view = api_view_class.as_view(api_module=info.module)
        urls.append(path(info.url_pattern, view))

    for info in page_info:
        view = page_view_class.as_view(page_path=info.path)
        urls.append(path(info.url_pattern, view))

    return path(prefix, include(urls))
