import dataclasses
from functools import cached_property, lru_cache
from importlib import import_module
from inspect import signature
from pathlib import Path
from types import ModuleType
from typing import Callable, List, Optional

from django import urls as urlconf
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class ExtConverter:
    regex = r"[a-z]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


urlconf.register_converter(ExtConverter, "__ext__")


def discover_routes() -> list:
    """Find file-based routes and return URLs for them."""
    dk_settings = settings.DJANGOKIT
    view_class = dk_settings.route_view_class

    urls = []
    tree = make_route_dir_tree()

    for node in tree:
        # Keep track of patterns that were already added for the node
        # so that each pattern is only added once.
        added_patterns = set()

        pattern = node.url_pattern
        view = view_class.as_view_from_node(
            node,
            cache_time=dk_settings.cache_time,
            private=dk_settings.private,
            vary_on=dk_settings.vary_on,
            template_name=node.page_template,
            cache_control=dk_settings.cache_control,
        )
        handlers = view.view_initkwargs["handlers"]

        if node.page_template:
            added_patterns.add(pattern)
            urls.append(urlconf.path(pattern, view, {"__subpath__": ""}))

        for method, method_handlers in handlers.items():
            for subpath, handler in method_handlers.items():
                assert subpath == handler.path

                if subpath == "":
                    subpattern = pattern
                elif pattern == "":
                    subpattern = subpath
                else:
                    subpattern = f"{pattern}/{subpath}"

                view_kwargs = {"__subpath__": subpath}

                if subpattern not in added_patterns:
                    added_patterns.add(subpattern)
                    urls.append(urlconf.path(subpattern, view, view_kwargs))

                ext_subpattern = f"{subpattern}.<__ext__:__ext__>"
                if ext_subpattern not in added_patterns:
                    added_patterns.add(ext_subpattern)
                    sig = signature(handler.impl)
                    if any(name == "__ext__" for name in sig.parameters):
                        urls.append(urlconf.path(ext_subpattern, view, view_kwargs))

    return urls


@lru_cache(maxsize=None)
def make_route_dir_tree(
    path: Optional[Path] = None, parent: Optional["RouteNode"] = None
) -> "RouteNode":
    """Make a tree of route directory info.

    Returns the root node of the tree.

    """
    root = settings.DJANGOKIT.routes_dir
    path = path or root
    directories = []
    file_names = []

    for entry in path.iterdir():
        name = entry.name
        if entry.is_file():
            file_names.append(name)
        elif entry.is_dir() and name != "__pycache__":
            directories.append(entry)

    if "page.html" in file_names:
        page_template_path = path / "page.html"
        page_template = str(page_template_path.relative_to(root))
    else:
        page_template = None

    handler_module_name = "handlers.py" if "handlers.py" in file_names else None
    node = RouteNode(parent, path, page_template, handler_module_name)

    directories = sorted(
        directories,
        key=lambda d: (
            1 if d.name.startswith("_") else 0,
            -len(d.name),
            d.name,
        ),
    )

    node.children = [make_route_dir_tree(directory, node) for directory in directories]
    return node


@dataclasses.dataclass
class RouteNode:
    """A node in the route tree containing info about a route."""

    parent: Optional["RouteNode"]

    path: Path
    """Absolute path to route directory."""

    page_template: Optional[str]
    """Page template, if present."""

    handler_module_name: Optional[str]
    """Name of handler module, if present."""

    children: List["RouteNode"] = dataclasses.field(default_factory=list)

    def __hash__(self):
        return hash(self.path)

    # Tree -------------------------------------------------------------

    @cached_property
    def root(self):
        current = self
        while True:
            parent = current.parent
            if parent is None:
                return current
            current = parent

    @cached_property
    def is_root(self):
        return self.parent is None

    @cached_property
    def depth(self):
        return 0 if self.is_root else len(self.rel_path.parts)

    def traverse(self, visit: Callable[["RouteNode"], None], node=None):
        """Traverse tree starting from specified node."""
        if node is None:
            node = self
        if visit is None:
            visit = self.default_visitor
        visit(node)
        for child in node.children:
            self.traverse(visit, child)

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

    # Route directory info ---------------------------------------------

    @cached_property
    def id(self) -> str:
        return "$root" if self.is_root else "_".join(self.rel_path.parts)

    @cached_property
    def rel_path(self) -> Path:
        """Relative path from root."""
        return self.path.relative_to(self.root.path)

    @cached_property
    def package_name(self) -> str:
        routes_package = settings.DJANGOKIT.routes_package
        if self.is_root:
            return routes_package
        package_name = ".".join(self.rel_path.parts)
        return f"{routes_package}.{package_name}"

    @cached_property
    def handler_module(self) -> Optional[ModuleType]:
        if not self.handler_module_name:
            return None
        name = Path(self.handler_module_name).stem
        qual_name = f"{self.package_name}.{name}"
        return import_module(qual_name)

    @cached_property
    def url_pattern(self) -> str:
        """Convert route path to Django URL pattern."""
        if self.is_root:
            return ""
        segments = []
        for part in self.rel_path.parts:
            if part.startswith("_"):
                name = part[1:]
                if name == "id":
                    segment = f"<int:{name}>"
                elif name == "slug":
                    segment = f"<slug:{name}>"
                elif name == "uuid":
                    segment = f"<uuid:{name}>"
                else:
                    segment = f"<{name}>"
                segments.append(segment)
            else:
                part = part.replace("_", "-")
                segments.append(part)
        pattern = "/".join(segments)
        return pattern

    def __str__(self):
        indent = " " * (self.depth * 4)
        path = self.path.relative_to(self.parent.path) if self.parent else "/"

        has = ", ".join(
            item
            for item in (
                "page template" if self.page_template else None,
                "handler module" if self.handler_module else None,
            )
            if item is not None
        )

        children = "\n\n".join(str(c) for c in self.children)
        children = f"[\n{children}\n{indent}]" if children else "[]"

        string = [
            f"{indent}path: {path}",
            f"pattern: {self.url_pattern}",
            f"has: {has}",
            f"children: {children}",
        ]

        return f"\n{indent}".join(string)
