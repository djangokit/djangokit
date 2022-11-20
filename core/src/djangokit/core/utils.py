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


@dataclass
class LayoutInfo:
    id: str

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
    info = []
    page_paths = root.glob("**/page.[jt]sx")

    for page_path in page_paths:
        rel_page_path = page_path.relative_to(root)
        route_path = rel_page_path.parent.as_posix()

        if route_path == ".":
            page_id = "root"
            import_path = "page"
            url_pattern = ""
            route_pattern = "/"
        else:
            page_id = route_path.replace("/", "_")
            import_path = f"{route_path}/page"
            segments = route_path.split("/")

            url_pattern = []
            route_pattern = []

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

        info.append(
            PageInfo(
                id=page_id,
                path=page_path,
                rel_path=rel_page_path,
                import_path=import_path,
                url_pattern=url_pattern,
                route_pattern=route_pattern,
            )
        )

    return info


def find_apis(root: Path, root_package: str) -> List[ApiInfo]:
    """Find API modules in directory."""
    info = []
    api_paths = root.glob("**/api.py")

    for api_path in api_paths:
        rel_api_path = api_path.relative_to(root)

        rel_path = rel_api_path.parent.as_posix()
        rel_path = "" if rel_path == "." else rel_path

        if rel_path:
            api_package_name = rel_path.replace("/", ".")
            module_name = f"{root_package}.{api_package_name}"

            segments = rel_path.split("/")
            for i, segment in enumerate(segments):
                if segment.startswith("[") and segment.endswith("]"):
                    segments[i] = f"<{segment[1:-1]}>"

            url_pattern = "/".join(segments)
            url_pattern = f"__api__/{url_pattern}"
        else:
            module_name = f"{root_package}.api"
            url_pattern = f"__api__/__root__"

        module = import_module(module_name)

        info.append(
            ApiInfo(
                module=module,
                url_pattern=url_pattern,
            )
        )

    return info
