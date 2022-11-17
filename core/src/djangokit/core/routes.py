from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List

from django.urls import path

from .utils import get_package_info
from .views import ApiView, PageView


def register_routes(
    package,
    page_view_class=PageView,
    api_view_class=ApiView,
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
    urls = []
    page_info = find_pages(package)
    api_info = find_apis(package)

    for info in page_info:
        view = page_view_class.as_view(page_path=info.path)
        urls.append(path(info.url_pattern, view))

    for info in api_info:
        view = api_view_class.as_view(api_module=info.module)
        urls.append(path(info.url_pattern, view))

    return urls


@dataclass
class PageInfo:

    path: Path
    """Path to page.jsx or page.tsx."""

    url_pattern: str
    """URL pattern for page."""


def find_pages(package) -> List[PageInfo]:
    info = []
    package_info = get_package_info(package)
    page_paths = package_info.path.glob("**/*.[jt]sx")

    for page_path in page_paths:
        rel_page_path = page_path.relative_to(package_info.path)

        rel_path = rel_page_path.parent.as_posix()
        rel_path = "" if rel_path == "." else rel_path

        segments = rel_path.rsplit("/", 1)

        for i, segment in enumerate(segments):
            if segment.startswith("[") and segment.endswith("]"):
                segments[i] = f"<{segment[1:-1]}>"

        url_pattern = "/".join(segments)

        info.append(PageInfo(
            path=page_path,
            url_pattern=url_pattern,
        ))

    return info


@dataclass
class ApiInfo:

    module: ModuleType
    """API module."""

    url_pattern: str
    """URL pattern for API module."""


def find_apis(package) -> List[ApiInfo]:
    """Find API modules in package."""
    info = []
    package_info = get_package_info(package)
    api_paths = package_info.path.glob("**/api.py")

    for api_path in api_paths:
        rel_api_path = api_path.relative_to(package_info.path)

        rel_path = rel_api_path.parent.as_posix()
        rel_path = "" if rel_path == "." else rel_path

        if rel_path:
            api_package_name = rel_path.replace("/", ".")
            module_name = f"{package_info.name}.{api_package_name}.api"
        else:
            module_name = f"{package_info.name}.api"

        module = import_module(module_name)

        segments = module_name.rsplit(".", 1)
        for i, segment in enumerate(segments):
            if segment.startswith("[") and segment.endswith("]"):
                segments[i] = f"<{segment[1:-1]}>"

        url_pattern = "/".join(segments)
        url_pattern = f"api/{url_pattern}"

        info.append(ApiInfo(
            module=module,
            url_pattern=url_pattern,
        ))

    return info
