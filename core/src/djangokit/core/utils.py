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
    """URL pattern for page."""


@dataclass
class ApiInfo:

    module: ModuleType
    """API module."""

    url_pattern: str
    """URL pattern for API module."""


def get_package_info(module: Union[ModuleType, str]) -> PackageInfo:
    """Get package info for the specified module.

    .. note::
        This gets info on the *package* containing the specified module
        rather than info on the module itself.

    Example::

        >>> info = get_package_info("djangokit.core.utils")
        >>> info.name
        'djangokit.core'
        >>> info.path.as_posix()
        '...djangokit/core'

    """
    if isinstance(module, str):
        module = import_module(module)
    package_name = module.__package__
    package_module = import_module(package_name)
    return PackageInfo(
        module=package_module, name=package_name, path=Path(module.__file__).parent
    )


def find_pages(package) -> List[PageInfo]:
    """Find pages in package."""
    info = []
    package_info = get_package_info(package)
    page_paths = package_info.path.glob("**/*.[jt]sx")

    for page_path in page_paths:
        rel_page_path = page_path.relative_to(package_info.path)

        rel_path = rel_page_path.parent.as_posix()
        rel_path = "" if rel_path == "." else rel_path

        segments = rel_path.rsplit("/", 1)

        for i, segment in enumerate(segments):
            if segment.startswith("[") and segment.endswith("]"):
                segments[i] = f"<{segment[1:-1]}>"

        url_pattern = "/".join(segments)

        info.append(
            PageInfo(
                path=page_path,
                url_pattern=url_pattern,
            )
        )

    return info


def find_apis(package) -> List[ApiInfo]:
    """Find API modules in package."""
    info = []
    package_info = get_package_info(package)
    api_paths = package_info.path.glob("**/api.py")

    for api_path in api_paths:
        rel_api_path = api_path.relative_to(package_info.path)

        rel_path = rel_api_path.parent.as_posix()
        rel_path = "" if rel_path == "." else rel_path

        if rel_path:
            api_package_name = rel_path.replace("/", ".")
            module_name = f"{package_info.name}.{api_package_name}.api"
        else:
            module_name = f"{package_info.name}.api"

        module = import_module(module_name)

        segments = module_name.rsplit(".", 1)
        for i, segment in enumerate(segments):
            if segment.startswith("[") and segment.endswith("]"):
                segments[i] = f"<{segment[1:-1]}>"

        url_pattern = "/".join(segments)
        url_pattern = f"api/{url_pattern}"

        info.append(
            ApiInfo(
                module=module,
                url_pattern=url_pattern,
            )
        )

    return info
