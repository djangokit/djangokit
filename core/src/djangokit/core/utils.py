from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List, Union


@dataclass
class PackageInfo:
    module: ModuleType
    """The package's module."""

    name: str
    """The package's dotted name."""

    path: Path
    """The package's directory path."""


@dataclass
class PageInfo:
    path: Path
    """Path to page.jsx or page.tsx."""

    url_pattern: str
    """Django URL pattern for page."""

    route_pattern: str
    """URL pattern for page."""


@dataclass
class ApiInfo:
    module: ModuleType
    """API module."""

    url_pattern: str
    """URL pattern for API module."""


def find_pages(root: Path) -> List[PageInfo]:
    """Find pages in root directory."""
    info = []
    page_paths = root.glob("**/*.[jt]sx")

    for page_path in page_paths:
        rel_page_path = page_path.relative_to(root)

        rel_path = rel_page_path.parent.as_posix()
        rel_path = "" if rel_path == "." else rel_path

        parts = rel_path.rsplit("/", 1)
        url_segments = []
        route_segments = []

        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                name = part[1:-1]
                url_part = f"<{name}>"
                url_segments.append(url_part)

                name_parts = name.split("_")
                for i in enumerate(name_parts[1:], 1):
                    name_parts[i] = name_parts[i].capitalize()

                route_part = f"{name}"
                route_segments.append(f":{route_part}")
            else:
                part = part.replace("_", "-")
                url_segments.append(part)
                route_segments.append(part)

        url_pattern = "/".join(url_segments)
        route_pattern = "/".join(route_segments)
        route_pattern = f"/{route_pattern}"

        info.append(
            PageInfo(
                path=page_path,
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
