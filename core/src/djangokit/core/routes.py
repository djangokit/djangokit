import dataclasses
import posixpath
from functools import cached_property, lru_cache
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from django import urls as urlconf
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .exceptions import RouteError
from .views import ApiView, PageView


def discover_routes(
    api_prefix,
    page_prefix,
    api_view_class=ApiView,
    page_view_class=PageView,
) -> list:
    """Find file-based page & API routes and return URLs for them.

    Finds page & API routes in the specified package and creates a view
    and URLconf for each.

    """
    all_urls = []
    api_urls = []
    page_urls = []
    tree = make_route_dir_tree()
    api_nodes = tree.collect_api_nodes()
    page_nodes = tree.collect_page_nodes()

    for node in api_nodes:
        api_module = node.api_module
        assert isinstance(api_module, ModuleType)

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
        pattern = node.url_pattern
        path_func = urlconf.re_path if pattern.startswith("^") else urlconf.path
        if pattern:
            api_urls.append(path_func(pattern, view))
        else:
            all_urls.append(path_func(api_prefix, view))

    for node in page_nodes:
        view = page_view_class.as_view(page_path=node.path)
        pattern = node.url_pattern
        path_func = urlconf.re_path if pattern.startswith("^") else urlconf.path
        if pattern:
            page_urls.append(path_func(pattern, view))
        else:
            all_urls.append(path_func(page_prefix, view))

    all_urls.append(urlconf.path(api_prefix, urlconf.include(api_urls)))
    all_urls.append(urlconf.path(page_prefix, urlconf.include(page_urls)))

    return all_urls


@lru_cache(maxsize=None)
def make_route_dir_tree(path=None, parent=None) -> "RouteDirNode":
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

    def has_tsx_or_jsx(stem: str) -> bool:
        return f"{stem}.tsx" in file_names or f"{stem}.jsx" in file_names

    has_layout = has_tsx_or_jsx("layout")
    has_nested_layout = has_tsx_or_jsx("nested-layout")
    has_page = has_tsx_or_jsx("page")
    has_error = has_tsx_or_jsx("error")
    has_api = "api.py" in file_names

    node = RouteDirNode(
        parent,
        path,
        has_layout,
        has_nested_layout,
        has_page,
        has_error,
        has_api,
    )

    if has_layout and has_nested_layout:
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
class RouteDirNode:

    parent: Optional["RouteDirNode"]
    path: Path
    has_layout: bool
    has_nested_layout: bool
    has_page: bool
    has_error: bool
    has_api: bool
    children: List["RouteDirNode"] = dataclasses.field(default_factory=list)

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

    def traverse(self, visit: Callable[["RouteDirNode"], None], node=None):
        """Traverse tree starting from specified node."""
        if node is None:
            node = self
        if visit is None:
            visit = self.default_visitor
        visit(node)
        for child in node.children:
            self.traverse(visit, child)

    def collect_page_nodes(self) -> List["RouteDirNode"]:
        """Traverse tree and collect all page nodes."""
        nodes = []
        self.traverse(lambda node: nodes.append(node) if node.has_page else None)
        return nodes

    def collect_api_nodes(self) -> List["RouteDirNode"]:
        """Traverse tree and collect all API nodes."""
        nodes = []
        self.traverse(lambda node: nodes.append(node) if node.has_api else None)
        return nodes

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
        if self.is_root:
            return settings.DJANGOKIT.routes_package
        package_name = ".".join(self.rel_path.parts)
        return f"{settings.DJANGOKIT.routes_package}.{package_name}"

    @cached_property
    def api_module(self) -> Optional[ModuleType]:
        if not self.has_api:
            return None
        module_name = f"{self.package_name}.api"
        return import_module(module_name)

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
            segments[-1] = ".*"
        pattern = "/".join(segments)
        if is_catchall:
            pattern = f"^{pattern}"
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
    def layout_for_nested_layout(self) -> Optional["RouteDirNode"]:
        """Find layout for nested layout node."""
        if not self.has_nested_layout:
            return None
        current = self.parent
        while current is not None:
            if current.has_layout or current.has_nested_layout:
                return current
            current = current.parent
        raise RouteError(
            "Could not find parent layout for nested layout " f"{self.rel_path}."
        )

    @cached_property
    def layout_for_page(self) -> Optional["RouteDirNode"]:
        """Find layout for page node."""
        if not self.has_page:
            return None
        current: Optional[RouteDirNode] = self
        while current is not None:
            if current.has_layout or current.has_nested_layout:
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

        def imp(node, component, segment, base_path=routes_path, join=posixpath.join):
            path = join(base_path, *node.rel_path.parts, segment)
            return f'import {{ default as {component}_{node.id} }} from "{path}";'

        def visitor(node: RouteDirNode):
            if node.has_layout:
                imports.append(imp(node, "Layout", "layout"))
            elif node.has_nested_layout:
                imports.append(imp(node, "NestedLayout", "nested-layout"))
            if node.has_error:
                imports.append(imp(node, "Error", "error"))
            if node.has_page:
                imports.append(imp(node, "Page", "page"))

        self.traverse(visitor)
        return "\n".join(imports) if join else imports

    def js_routes(self, serialize=True) -> Union[str, List]:
        """Get JS route array."""
        top = []
        layouts: Dict[Path, Dict[str, Any]] = {}

        @dataclasses.dataclass
        class Element:
            type: Literal["Layout", "NestedLayout", "Error", "Page"]
            id: str

        def visitor(node: RouteDirNode):
            if node.has_layout or node.has_nested_layout:
                if node.has_nested_layout:
                    path = node.route_pattern_for_nested_layout
                    element = Element("NestedLayout", node.id)
                else:
                    path = node.route_pattern
                    element = Element("Layout", node.id)

                layout = {"path": path, "element": element}

                if node.has_error:
                    layout["errorElement"] = Element("Error", node.id)

                layout["children"] = children = []

                if node.has_page:
                    children.append({"path": "", "element": Element("Page", node.id)})

                if node.has_nested_layout:
                    parent_layout = node.layout_for_nested_layout
                    assert parent_layout
                    layout_info = layouts[parent_layout.rel_path]
                    layout_info["children"].append(layout)
                else:
                    top.append(layout)

                layouts[node.rel_path] = layout

            elif node.has_page:
                page_layout = node.layout_for_page
                page = {"path": "", "element": Element("Page", node.id)}
                if node.has_error:
                    page["errorElement"] = Element("Error", node.id)
                if page_layout is None:
                    page["path"] = node.route_pattern
                    top.append(page)
                else:
                    page["path"] = node.route_pattern_for_page
                    layout_info = layouts[page_layout.rel_path]
                    layout_info["children"].append(page)

        self.traverse(visitor)

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
                "layout" if self.has_layout else None,
                "nested layout" if self.has_nested_layout else None,
                "page" if self.has_page else None,
                "error" if self.has_error else None,
                "api" if self.has_api else None,
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
