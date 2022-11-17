from django.urls import include, path

from .conf import get_setting
from .utils import find_apis, find_pages
from .views import ApiView, PageView


def create_routes(
    prefix="",
    package=None,
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
    if package is None:
        package = f"{get_setting('package')}.routes"

    urls = []
    page_info = find_pages(package)
    api_info = find_apis(package)

    for info in page_info:
        view = page_view_class.as_view(page_path=info.path)
        urls.append(path(info.url_pattern, view))

    for info in api_info:
        view = api_view_class.as_view(api_module=info.module)
        urls.append(path(info.url_pattern, view))

    return path(prefix, include(urls))
