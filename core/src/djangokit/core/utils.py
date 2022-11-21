import os
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List, Optional


@dataclass
class PageInfo:
    id: str

    path: Path
    """Absolute path to Page component module."""

    rel_path: Path
    """Path to Page component module relative to routes/."""

    import_path: str
    """JS import path of Page component module relative to routes/.

    `routes/page` (root) -> "page"
    `routes/_id/page` -> "_id/page".

    """

    url_pattern: str
    """Django URL pattern for page.
    
    `routes/page` (root) -> ""
    `routes/_id/page` -> "<id>".
    
    """

    route_pattern: str
    """React Router URL pattern for page.
    
    `routes/page` (root) -> "/"
    `routes/_id/page` -> ":id".
    
    """

    @classmethod
    def from_path(cls, path: Path, root: Path) -> "PageInfo":
        assert path.is_file()
        assert path.name == "page.tsx" or path.name == "page.jsx"
        assert path.is_relative_to(root)

        rel_path = path.relative_to(root)
        route_path = rel_path.parent.as_posix()

        if route_path == ".":
            page_id = "root"
            import_path = "page"
            url_pattern = ""
            route_pattern = "/"
        else:
            page_id = route_path.replace("/", "_")
            import_path = f"{route_path}/page"
            url_pattern = []
            route_pattern = []

            segments = route_path.split("/")
            for segment in segments:
                if segment.startswith("_"):
                    name = segment[1:]
                    url_segment = f"<{name}>"
                    url_pattern.append(url_segment)

                    name_parts = name.split("_")
                    for i in enumerate(name_parts[1:], 1):
                        name_parts[i] = name_parts[i].capitalize()

                    route_segment = f"{name}"
                    route_pattern.append(f":{route_segment}")
                else:
                    segment = segment.replace("_", "-")
                    url_pattern.append(segment)
                    route_pattern.append(segment)

            url_pattern = "/".join(url_pattern)
            route_pattern = "/".join(route_pattern)
            route_pattern = f"/{route_pattern}"

        return cls(
            id=page_id,
            path=path,
            rel_path=rel_path,
            import_path=import_path,
            url_pattern=url_pattern,
            route_pattern=route_pattern,
        )


@dataclass
class LayoutInfo:
    id: str

    path: Path
    """Absolute path to Layout component module."""

    import_path: str
    """JS import path of Layout component module relative to routes/.

    `routes/layout` (root) -> "layout"

    """

    children: List[PageInfo]
    """Pages using this layout."""


@dataclass
class ApiInfo:
    module: ModuleType
    """API module."""

    url_pattern: str
    """URL pattern for API module."""

    @classmethod
    def from_path(cls, path: Path, root: Path, root_package: str) -> "ApiInfo":
        """Make an ApiInfo instance from a file system path.

        Args:
            path: Path to an API module in a file named api.py
            root: Path to the root of the API/routes hierarchy
            root_package: Package name of root

        Example::

            .../src/package/routes/
                api.py
                _id/
                    api.py

            ApiInfo.from_path(
                ".../src/package/routes/api.py",
                ".../src/package/routes",
                "package.routes",
            )
            # -> ApiInfo(module="package.routes.api", url_pattern="$api/__root__")

            ApiInfo.from_path(
                ".../src/package/routes/_id/api.py",
                ".../src/package/routes",
                "package.routes",
            )
            # -> ApiInfo(module="package.routes._id.api", url_pattern="$api/<id>")

        """
        assert path.is_file()
        assert path.name == "api.py"
        assert path.is_relative_to(root)

        rel_path = path.relative_to(root)
        package_path = rel_path.parent.as_posix()

        if package_path == ".":
            module_name = f"{root_package}.api"
            url_pattern = "$api"
        else:
            package_name = package_path.replace("/", ".")
            module_name = f"{root_package}.{package_name}.api"

            segments = package_path.split("/")
            for i, segment in enumerate(segments):
                if segment.startswith("_"):
                    segments[i] = f"<{segment[1:]}>"

            url_pattern = "/".join(segments)
            url_pattern = f"$api/{url_pattern}"

        module = import_module(module_name)
        return cls(module=module, url_pattern=url_pattern)


def make_page_tree(root: Path):
    root_layout = get_layout(root, root)

    if root_layout is None:
        root_layout = LayoutInfo(id="root", path=None, import_path=None, children=[])

    current_layout = root_layout

    for entry in root.iterdir():
        pass

    return root_layout


def get_layout(directory: Path, root: Path) -> Optional[LayoutInfo]:
    layout_id = "_".join(directory.relative_to(root).parts)
    import_path = directory.relative_to(root) / "layout"

    layout_path = directory / "layout.tsx"
    if layout_path.exists():
        return LayoutInfo(
            id=layout_id, path=layout_path, import_path=import_path, children=[]
        )

    layout_path = directory / "layout.jsx"
    if layout_path.exists():
        return LayoutInfo(
            id=layout_id, path=layout_path, import_path=import_path, children=[]
        )

    return None


def find_layout(root: Path, page_path: Path) -> Optional[Path]:
    """Find layout for page."""
    parent = page_path.parent
    assert parent.is_relative_to(root), "Page path must be under root path"
    while True:
        candidates = (parent / "layout.tsx", parent / "layout.jsx")
        for candidate in candidates:
            if candidate.exists():
                return candidate
        parent.samefile(root)
        if parent.samefile(root):
            return None
        parent = parent.parent


def find_pages(root: Path) -> List[PageInfo]:
    """Find pages in root directory."""
    paths = root.glob("**/page.[jt]sx")
    return [PageInfo.from_path(path, root) for path in paths]


def find_apis(root: Path, root_package: str) -> List[ApiInfo]:
    """Find API modules in directory."""
    paths = root.glob("**/api.py")
    return [ApiInfo.from_path(path, root, root_package) for path in paths]
