import posixpath
from dataclasses import dataclass, field
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

    layout_route_pattern: Optional[str] = None
    """React Router URL pattern for page relative to layout."""

    def __hash__(self):
        return id(self)

    @classmethod
    def from_path(cls, path: Path, root: Path) -> "PageInfo":
        """Make a PageInfo instance from a file system path."""
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
            url_pattern = get_url_pattern(route_path)
            route_pattern = get_route_pattern(route_path)

        return cls(
            id=page_id,
            path=path,
            rel_path=rel_path,
            import_path=import_path,
            url_pattern=url_pattern,
            route_pattern=route_pattern,
        )

    @classmethod
    def from_dir(cls, directory: Path, root: Path) -> Optional["PageInfo"]:
        """Make a PageInfo instance from a file system directory path.

        This searches for a page module in the specified directory.

        """
        assert directory.is_dir()
        assert directory.is_relative_to(root)
        path = directory / "page.tsx"
        if path.exists():
            return cls.from_path(path, root)
        path = directory / "page.jsx"
        if path.exists():
            return cls.from_path(path, root)
        return None


@dataclass
class LayoutInfo:
    id: str

    path: Path
    """Absolute path to Layout component module."""

    import_path: str
    """JS import path of Layout component module relative to routes/.

    `routes/layout` (root) -> "layout"

    """

    route_pattern: str
    """React Router URL pattern for layout.
    
    `routes/layout` (root) -> "/"
    `routes/_id/layout` -> ":id".
    
    """

    children: List[PageInfo] = field(default_factory=list)
    """Pages using this layout."""

    def __hash__(self):
        return id(self)

    @classmethod
    def from_path(cls, path: Path, root: Path) -> "LayoutInfo":
        """Make a LayoutInfo instance from a file system path."""
        assert path.is_file()
        assert path.name == "layout.tsx" or path.name == "layout.jsx"
        assert path.is_relative_to(root)

        rel_path = path.relative_to(root)
        route_path = rel_path.parent.as_posix()

        if route_path == ".":
            layout_id = "root"
            import_path = "layout"
            route_pattern = "/"
        else:
            layout_id = route_path.replace("/", "_")
            import_path = f"{route_path}/layout"
            route_pattern = get_route_pattern(route_path)

        return cls(
            id=layout_id,
            path=path,
            import_path=import_path,
            route_pattern=route_pattern,
        )

    @classmethod
    def from_dir(cls, directory: Path, root: Path) -> Optional["LayoutInfo"]:
        """Make a LayoutInfo instance from a file system directory path.

        This searches for a layout module in the specified directory.

        """
        assert directory.is_dir()
        assert directory.is_relative_to(root)
        path = directory / "layout.tsx"
        if path.exists():
            return LayoutInfo.from_path(path, root)
        path = directory / "layout.jsx"
        if path.exists():
            return LayoutInfo.from_path(path, root)
        return None


@dataclass
class ApiInfo:
    module: ModuleType
    """API module."""

    url_pattern: str
    """URL pattern for API module."""

    def __hash__(self):
        return id(self)

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
            url_pattern = get_url_pattern(package_path)
            url_pattern = f"$api/{url_pattern}"

        module = import_module(module_name)
        return cls(module=module, url_pattern=url_pattern)


def get_url_pattern(route_path: str) -> str:
    """Convert relative path to Django URL pattern."""
    assert not posixpath.isabs(route_path)
    url_pattern = []
    segments = route_path.split("/")
    for segment in segments:
        if segment.startswith("_"):
            name = segment[1:]
            segment = f"<{name}>"
            url_pattern.append(segment)
        else:
            segment = segment.replace("_", "-")
            url_pattern.append(segment)
    url_pattern = "/".join(url_pattern)
    return url_pattern


def get_route_pattern(route_path: str) -> str:
    """Convert relative path to React Router URL pattern."""
    assert not posixpath.isabs(route_path)
    route_pattern = []
    segments = route_path.split("/")
    for segment in segments:
        if segment.startswith("_"):
            name = segment[1:]
            name_parts = name.split("_")
            for i in enumerate(name_parts[1:], 1):
                name_parts[i] = name_parts[i].capitalize()
            route_segment = f"{''.join(name_parts)}"
            route_pattern.append(f":{route_segment}")
        else:
            segment = segment.replace("_", "-")
            route_pattern.append(segment)
    route_pattern = "/".join(route_pattern)
    route_pattern = f"/{route_pattern}"
    return route_pattern
