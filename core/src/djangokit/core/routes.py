import posixpath
from functools import lru_cache
from os import path
from pathlib import Path, PosixPath
from typing import List

from django.urls import path

from .conf import settings
from .dataclasses import ApiInfo, LayoutInfo, PageInfo
from .exceptions import BuildError
from .views import ApiView, PageView
from .views import csrf as csrf_views
from .views import user as user_views


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
    urls = [
        path("$api/csrf-token", csrf_views.get_token),
        path("$api/current-user", user_views.get_current_user),
    ]

    page_info = find_pages(settings.routes_dir)
    api_info = find_apis(settings.routes_dir, settings.routes_package)

    for info in api_info:
        view = api_view_class.as_view(api_module=info.module)
        urls.append(path(info.url_pattern, view))

    for info in page_info:
        view = page_view_class.as_view(page_path=info.path)
        urls.append(path(info.url_pattern, view))

    return urls


def info_sorter(info):
    """Key function for sorting info objects by URL pattern.

    This can be used to sort info objects by URL pattern using the
    following rules:

    1. Patterns with more segments sort first
    2. Segments in a given position are sorted using the following
       rules:
        1. Literal segments sort before pattern segments
        2. Longer segments sort before shorter segments
        3. Equal length segments are sorted lexicographically

    The general idea is to force longer URLs to match before shorter
    URLs and to prefer literal segments over pattern matching.

    """
    url_pattern = PosixPath(info.url_pattern)
    parts = url_pattern.parts
    return (-len(parts),) + tuple(
        (
            part.startswith("<"),
            -len(part),
            part,
        )
        for part in parts
    )


def find_pages(root: Path) -> List[PageInfo]:
    """Find pages in root directory."""
    paths = root.glob("**/page.[jt]sx")
    info = [PageInfo.from_path(page_path, root) for page_path in paths]
    info.sort(key=info_sorter)
    return info


def find_apis(root: Path, root_package: str) -> List[ApiInfo]:
    """Find API modules in directory."""
    paths = root.glob("**/api.py")
    info = [ApiInfo.from_path(api_path, root, root_package) for api_path in paths]
    info.sort(key=info_sorter)
    return info


@lru_cache
def get_route_info(
    directory: Path,
    *,
    root=None,
    parent_layout=None,
) -> LayoutInfo:
    """Get route info for routes in directory, recursively.

    This organizes pages under their respective layouts.

    """
    if root is None:
        is_root = True
        root = directory
    else:
        is_root = False

    layout = LayoutInfo.from_dir(directory, root)

    if not layout:
        if is_root:
            raise BuildError(
                f"A root layout is required but no layout component was "
                f"found in {root} (searched for layout.jsx and layout.tsx)"
            )
        else:
            layout = parent_layout

    page = PageInfo.from_dir(directory, root)
    if page:
        layout_route_pattern = posixpath.relpath(
            page.route_pattern,
            layout.route_pattern,
        )
        if layout_route_pattern == ".":
            layout_route_pattern = ""
        page.layout_route_pattern = layout_route_pattern
        layout.children.append(page)

    for entry in directory.iterdir():
        if entry.is_dir() and not entry.name.startswith("__"):
            nested_layout = get_route_info(entry, root=root, parent_layout=layout)
            if nested_layout is not layout:
                layout.children.append(nested_layout)

    return layout
