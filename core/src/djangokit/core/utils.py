from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Union


@dataclass
class PackageInfo:

    module: ModuleType
    """The package's module."""

    name: str
    """The package's dotted name."""

    path: Path
    """The package's directory path."""


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
        module=package_module,
        name=package_name,
        path=Path(module.__file__).parent
    )
