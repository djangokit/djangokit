import dataclasses
import posixpath
from functools import cached_property, lru_cache
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from django import urls as urlconf
from django.conf import settings

from .exceptions import RouteError


def discover_routes(view_class=None, cache_time=None) -> list:
    """Find file-based routes and return URLs for them."""
    dk_settings = settings.DJANGOKIT

    if view_class is None:
        view_class = dk_settings.route_view_class

    if cache_time is None:
        cache_time = dk_settings.cache_time

    urls = []
    tree = make_route_dir_tree()

    for node in tree:
        subpaths = set()
        pattern = node.url_pattern
        view = view_class.as_view_from_node(node, cache_time=cache_time)
        handlers = view.view_initkwargs["handlers"]

        if node.page_module:
            subpaths.add("")
            urls.append(urlconf.path(pattern, view, {"__subpath__": ""}))

        for method, method_handlers in handlers.items():
            for subpath, handler in method_handlers.items():
                assert subpath == handler.path
                if subpath not in subpaths:
                    subpaths.add(subpath)
                    if subpath == "":
                        subpattern = pattern
                    elif pattern == "":
                        subpattern = subpath
                    else:
                        subpattern = f"{pattern}/{subpath}"
                    conf = urlconf.path(subpattern, view, {"__subpath__": subpath})
                    urls.append(conf)

    return urls


@lru_cache(maxsize=None)
def make_route_dir_tree(path=None, parent=None) -> "RouteNode":
    """Make a tree of route directory info.

    Returns the root node of the tree.

    """
    if path is None:
        path = settings.DJANGOKIT.routes_dir

    directories = []
    file_names = []

    for entry in path.iterdir():
        name = entry.name
        if entry.is_file():
            file_names.append(name)
        elif entry.is_dir() and name != "__pycache__":
            directories.append(entry)

    def get_tsx_or_jsx_module(stem: str) -> Optional[str]:
        candidates = [f"{stem}.tsx", f"{stem}.jsx"]
        for candidate in candidates:
            if candidate in file_names:
                return candidate
        return None

    layout_module = get_tsx_or_jsx_module("layout")
    nested_layout_module = get_tsx_or_jsx_module("nested-layout")
    page_module = get_tsx_or_jsx_module("page")
    error_module = get_tsx_or_jsx_module("error")
    handler_module_name = "handlers.py" if "handlers.py" in file_names else None

    node = RouteNode(
        parent,
        path,
        layout_module,
        nested_layout_module,
        page_module,
        error_module,
        handler_module_name,
    )

    if layout_module and nested_layout_module:
        raise RouteError(
            "Found both a root layout and a nested layout for route "
            f"{node.rel_path}. Only one type of layout is allowed per "
            "route."
        )

    directories = sorted(
        directories,
        key=lambda d: (
            1 if d.name == "catchall" else 0,
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

    layout_module: Optional[str]
    """Name of layout module, if present."""

    nested_layout_module: Optional[str]
    """Name of nested layout module, if present."""

    page_module: Optional[str]
    """Name of page module, if present."""

    error_module: Optional[str]
    """Name of error module, if present."""

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
    def is_catchall(self) -> bool:
        return self.id == "catchall"

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
        is_catchall = self.is_catchall
        for part in self.rel_path.parts:
            if part.startswith("_"):
                name = part[1:]
                if is_catchall:
                    part = rf"(?P<{name}>[^/]+)"
                else:
                    part = f"<{name}>"
                segments.append(part)
            else:
                part = part.replace("_", "-")
                segments.append(part)
        if is_catchall:
            segments[-1] = "<path:path>"
        pattern = "/".join(segments)
        return pattern

    @cached_property
    def route_pattern(self) -> str:
        """Convert route path to React Router URL pattern."""
        if self is self.root:
            return "/"
        segments = []
        for part in self.rel_path.parts:
            if part.startswith("_"):
                name = part[1:]
                name_parts = name.split("_")
                name_parts = [name_parts[0]] + [p.capitalize() for p in name_parts[1:]]
                segment = f"{''.join(name_parts)}"
                segments.append(f":{segment}")
            else:
                part = part.replace("_", "-")
                segments.append(part)
        if self.is_catchall:
            segments[-1] = "*"
        pattern = "/".join(segments)
        pattern = f"/{pattern}"
        return pattern

    @cached_property
    def layout_for_nested_layout(self) -> Optional["RouteNode"]:
        """Find layout for nested layout node."""
        if not self.nested_layout_module:
            return None
        current = self.parent
        while current is not None:
            if current.layout_module or current.nested_layout_module:
                return current
            current = current.parent
        raise RouteError(
            "Could not find parent layout for nested layout " f"{self.rel_path}."
        )

    @cached_property
    def layout_for_page(self) -> Optional["RouteNode"]:
        """Find layout for page node."""
        if not self.page_module:
            return None
        current: Optional[RouteNode] = self
        while current is not None:
            if current.layout_module or current.nested_layout_module:
                return current
            current = current.parent
        raise RouteError(f"Could not find layout for page {self.rel_path}.")

    def _layout_pattern(self, kind: Literal["nested-layout", "page"]) -> str:
        if self.is_root:
            return self.route_pattern
        if kind == "nested-layout":
            layout = self.layout_for_nested_layout
        elif kind == "page":
            layout = self.layout_for_page
        else:
            raise ValueError(kind)
        assert layout
        pattern = posixpath.relpath(self.route_pattern, layout.route_pattern)
        if pattern == ".":
            pattern = ""
        return pattern

    @cached_property
    def route_pattern_for_nested_layout(self) -> str:
        """Convert route path to layout-relative URL pattern."""
        return self._layout_pattern("nested-layout")

    @cached_property
    def route_pattern_for_page(self) -> str:
        """Convert route path to layout-relative URL pattern."""
        return self._layout_pattern("page")

    def js_imports(self, routes_path: str, join=True) -> Union[List[str], str]:
        """Get JS imports for node including imports for child nodes."""
        imports = []

        def imp(node_, component, segment):
            path = posixpath.join(routes_path, *node_.rel_path.parts, segment)
            return f'import {{ default as {component}_{node_.id} }} from "{path}";'

        for node in self:
            if node.layout_module:
                imports.append(imp(node, "Layout", "layout"))
            elif node.nested_layout_module:
                imports.append(imp(node, "NestedLayout", "nested-layout"))
            if node.error_module:
                imports.append(imp(node, "Error", "error"))
            if node.page_module:
                imports.append(imp(node, "Page", "page"))

        return "\n".join(imports) if join else imports

    def js_routes(self, serialize=True) -> Union[str, List]:
        """Get JS route array."""
        top = []
        layouts: Dict[Path, Dict[str, Any]] = {}

        @dataclasses.dataclass
        class Element:
            type: Literal["Layout", "NestedLayout", "Error", "Page"]
            id: str

        for node in self:
            if node.layout_module or node.nested_layout_module:
                if node.nested_layout_module:
                    path = node.route_pattern_for_nested_layout
                    element = Element("NestedLayout", node.id)
                else:
                    path = node.route_pattern
                    element = Element("Layout", node.id)

                layout = {"path": path, "element": element}

                if node.error_module:
                    layout["errorElement"] = Element("Error", node.id)

                layout["children"] = children = []

                if node.page_module:
                    children.append({"path": "", "element": Element("Page", node.id)})

                if node.nested_layout_module:
                    parent_layout = node.layout_for_nested_layout
                    assert parent_layout
                    layout_info = layouts[parent_layout.rel_path]
                    layout_info["children"].append(layout)
                else:
                    top.append(layout)

                layouts[node.rel_path] = layout

            elif node.page_module:
                page_layout = node.layout_for_page
                page = {"path": "", "element": Element("Page", node.id)}
                if node.error_module:
                    page["errorElement"] = Element("Error", node.id)
                if page_layout is None:
                    page["path"] = node.route_pattern
                    top.append(page)
                else:
                    page["path"] = node.route_pattern_for_page
                    layout_info = layouts[page_layout.rel_path]
                    layout_info["children"].append(page)

        if not serialize:
            return top

        def serializer(obj):
            if isinstance(obj, dict):
                entries = [f"{k}: {serializer(v)}" for k, v in obj.items()]
                entries = ",".join(entries)
                return "".join(("{", entries, "}"))
            elif isinstance(obj, list):
                items = [serializer(item) for item in obj]
                items = ",".join(items)
                return f"[{items}]"
            elif isinstance(obj, str):
                return f'"{obj}"'
            elif isinstance(obj, Element):
                return f"<{obj.type}_{obj.id} />"
            type_ = obj.__class__.__name__
            raise TypeError(f"Unexpected object type: {type_}")

        return serializer(top)

    def __str__(self):
        indent = " " * (self.depth * 4)
        path = self.path.relative_to(self.parent.path) if self.parent else "/"

        has = ", ".join(
            item
            for item in (
                "layout" if self.layout_module else None,
                "nested layout" if self.nested_layout_module else None,
                "page" if self.page_module else None,
                "error" if self.error_module else None,
                "handler module" if self.handler_module else None,
            )
            if item is not None
        )

        children = "\n\n".join(str(c) for c in self.children)
        children = f"[\n{children}\n{indent}]" if children else "[]"

        string = [
            f"{indent}path: {path}",
            f"has: {has}",
            f"children: {children}",
        ]

        return f"\n{indent}".join(string)
