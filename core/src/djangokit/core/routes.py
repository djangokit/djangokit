import posixpath
from functools import lru_cache
from pathlib import Path, PosixPath
from typing import List

from django.core.exceptions import ImproperlyConfigured
from django.urls import path, re_path

from .conf import settings
from .dataclasses import ApiInfo, LayoutInfo, PageInfo
from .exceptions import BuildError
from .views import ApiView, PageView
from .views import user as user_views


def discover_routes(page_view_class=PageView, api_view_class=ApiView) -> list:
    """Find file-based page & API routes and return URLs for them.

    Finds page & API routes in the specified package and creates a view
    and URLconf for each.

    Usage in a typical DjangoKit project::

        # src/<package>/urls.py
        from django.contrib import admin
        from django.urls import include, path
        from djangokit.core import discover_routes

        urlpatterns = [
            path("", include(discover_routes())),
            path("$admin/", admin.site.urls),
        ]

    """
    urls = [
        path("$api/current-user", user_views.get_current_user),
    ]

    page_info = find_pages(settings.routes_dir)
    api_info = find_apis(settings.routes_dir, settings.routes_package)

    for info in api_info:
        api_module = info.module

        allowed_methods = {}
        for name in dir(api_module):
            if name in ApiView.http_method_names:
                allowed_methods[name] = getattr(api_module, name)
        if "head" not in allowed_methods and "get" in allowed_methods:
            allowed_methods["head"] = allowed_methods["get"]
        if not allowed_methods:
            raise ImproperlyConfigured(
                f"The API module {api_module.__name__} doesn't contain "
                "any handlers. Expected at least one of get, post, or "
                "some other handler."
            )

        view = api_view_class.as_view(
            api_module=api_module,
            allowed_methods=allowed_methods,
        )
        pattern = info.url_pattern
        path_func = re_path if pattern.startswith("^") else path
        urls.append(path_func(pattern, view))

    for info in page_info:
        view = page_view_class.as_view(page_path=info.path)
        pattern = info.url_pattern
        path_func = re_path if pattern.startswith("^") else path
        urls.append(path_func(pattern, view))

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
    3. The catchall route sorts last

    The general idea is to force longer URLs to match before shorter
    URLs and to prefer literal segments over pattern matching.

    """
    url_pattern = PosixPath(info.url_pattern)
    parts = url_pattern.parts
    key = [
        1 if info.id == "catchall" else 0,
        -len(parts),
    ]
    for part in parts:
        key.append(
            (
                part.startswith("<"),
                -len(part),
                part,
            )
        )
    return key


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


@lru_cache(maxsize=None)
def get_route_info(
    directory: Path,
    *,
    root=None,
    parent_layout=None,
    prefix=None,
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

    if layout:
        pattern = layout.route_pattern
        if not is_root:
            layout.route_pattern = posixpath.relpath(pattern, prefix)
        if prefix is None:
            prefix = pattern
        else:
            prefix = posixpath.join("/", prefix.rstrip("/"), pattern.lstrip("/"))
    elif is_root:
        raise BuildError(
            "A root layout is required but no layout component "
            f"was found in {root} (searched for layout.jsx and "
            f"layout.tsx)."
        )
    else:
        layout = parent_layout

    page = PageInfo.from_dir(directory, root)

    if page:
        rel_pattern = posixpath.relpath(page.route_pattern, prefix)
        if rel_pattern == ".":
            rel_pattern = ""
        page.route_pattern = rel_pattern.lstrip("/")
        layout.children.append(page)

    for entry in directory.iterdir():
        if entry.is_dir() and not entry.name.startswith("__"):
            nested_layout = get_route_info(
                entry,
                root=root,
                parent_layout=layout,
                prefix=prefix,
            )
            if nested_layout is not layout:
                layout.children.append(nested_layout)

    return layout
