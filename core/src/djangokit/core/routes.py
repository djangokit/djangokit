import posixpath
from functools import lru_cache
from os import path
from pathlib import Path
from typing import List

from django.urls import path

from .conf import settings
from .dataclasses import ApiInfo, LayoutInfo, PageInfo
from .exceptions import BuildError
from .views import ApiView, PageView


@lru_cache
def get_route_urls(page_view_class=PageView, api_view_class=ApiView) -> list:
    """Find file-based page & API routes and return URLs for them.

    Finds page & API routes in the specified package and creates a
    Django URL path for each.

    Usage in a typical DjangoKit project::

        # src/<package>/urls.py
        from django.contrib import admin
        from django.urls import include, path
        from djangokit.core import get_route_urls

        urlpatterns = [
            path("", include(get_route_urls())),
            path("$admin/", admin.site.urls),
        ]

    """
    urls = []
    page_info = find_pages(settings.routes_dir)
    api_info = find_apis(settings.routes_dir, settings.routes_package)

    for info in api_info:
        view = api_view_class.as_view(api_module=info.module)
        urls.append(path(info.url_pattern, view))

    for info in page_info:
        view = page_view_class.as_view(page_path=info.path)
        urls.append(path(info.url_pattern, view))

    return urls


def find_pages(root: Path) -> List[PageInfo]:
    """Find pages in root directory."""
    paths = root.glob("**/page.[jt]sx")
    return [PageInfo.from_path(page_path, root) for page_path in paths]


def find_apis(root: Path, root_package: str) -> List[ApiInfo]:
    """Find API modules in directory."""
    paths = root.glob("**/api.py")
    return [ApiInfo.from_path(api_path, root, root_package) for api_path in paths]


@lru_cache
def get_route_info(
    directory: Path,
    *,
    root=None,
    parent_layout=None,
) -> List[LayoutInfo]:
    """Get route info for routes in directory, recursively.

    This organizes pages under their respective layouts.

    """
    routes = []

    if root is None:
        is_root = True
        root = directory
    else:
        is_root = False

    layout = LayoutInfo.from_dir(directory, root)

    if layout:
        routes.append(layout)
    elif is_root:
        raise BuildError(
            f"A root layout is required but no layout component was "
            f"found in {root} (searched for layout.tsx and layout.jsx)"
        )
    else:
        layout = parent_layout

    page = PageInfo.from_dir(directory, root)
    if page:
        if page.route_pattern == layout.route_pattern:
            layout_route_pattern = ""
        else:
            layout_route_pattern = posixpath.relpath(
                page.route_pattern,
                layout.route_pattern,
            )
        page.layout_route_pattern = layout_route_pattern
        layout.children.append(page)

    for entry in directory.iterdir():
        if entry.is_dir() and entry.name != "__pycache__":
            routes.extend(get_route_info(entry, root=root, parent_layout=layout))

    return routes
