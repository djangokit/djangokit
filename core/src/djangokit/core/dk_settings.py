from dataclasses import asdict, dataclass, field
from importlib import import_module
from pathlib import Path
from socket import gethostname
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


@dataclass
class DjangoKitSettings:
    """DjangoKit settings.

    This defines the available DjangoKit settings, their types, and
    their default values. It also contains a number of attributes
    derived from the DjangoKit settings.

    """

    package: str
    """Top level package name of the DjangoKit app."""

    app_label: str
    """App label for the DjangoKit app (often the same as `package`)."""

    prefix: str = ""
    """URL mount point for the DjangoKit app, relative to site root."""

    admin_prefix: str = "$admin/"
    """Path to Django Admin, relative to `prefix`."""

    current_user_path: str = "$current-user"
    """Path to current user endpoint, relative to `prefix`."""

    intercept_extensions: Optional[Dict[str, str]] = None
    """URL extensions to intercept.

    Map of extension to content type::

        # settings.public.toml
        [djangokit.intercept_extensions]
        ".json" = "application/json"
        ".geojson" = "application/geo+json"

    If set, GET and HEAD requests with a path that ends with one of the
    specified extensions will be intercepted and modified as follows:
    
    1. The extension will be stripped from path and path_info
    2. The Accept header will be set to the specified content type

    """

    cache_time: Optional[int] = None
    """How long to cache responses for GETs, in seconds.

    This is coarse-grained caching that will apply to *all* GET requests
    for *all* routes (both pages and handlers).

    """

    # Additional cache settings
    private: Optional[bool] = None
    vary_on: Optional[Sequence[str]] = ("Accept",)
    cache_control: Optional[dict] = None

    title: str = "A DjangoKit Site"
    """Site title (used for `<title>`)"""

    description: str = "A website made with DjangoKit"
    """Site description (used for `<meta name="description">`)"""

    global_stylesheets: List[str] = field(default_factory=lambda: ["global.css"])
    """Global stylesheets to be injected into the document `<head>`."""

    route_view_class: Union[str, type] = "djangokit.core.RouteView"
    """The view class used for routes.
    
    It's expected to have an `as_view_from_node` method that takes a
    :class:`RouteNode` and, optionally, a `template_name`, `cache_time`,
    and/or `ssr_bundle_path` and returns a view (e.g., by calling
    `cls.as_view()`).
    
    """

    current_user_serializer: Union[str, Callable] = (
        "djangokit.core.user.current_user_serializer"
    )
    """Serializer function used to serialize the current user."""

    csr: bool = True
    """Whether CSR is enabled."""

    ssr: bool = True
    """Whether SSR is enabled."""

    webmaster: str = field(default_factory=lambda: f"webmaster@{gethostname()}")
    """Email address of the webmaster / site admin."""

    noscript_message: str = (
        "This site requires JavaScript to be enabled in your browser."
    )
    """Message to display when browser JS is disabled.
    
    Can be set to "" to disable showing a noscript message.
    
    """

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "package":
            package = value
            module = import_module(package)
            paths = module.__path__
            if len(paths) > 1:
                raise ImproperlyConfigured(
                    f"DjangoKit app package {package} appears to be a "
                    "namespace package because it resolves to multiple "
                    "file system paths. You might need to add an "
                    "__init__.py to the package."
                )
            package_dir = Path(paths[0])
            self.package_dir = package_dir
            self.app_dir = package_dir / "app"
            self.models_dir = package_dir / "models"
            self.routes_dir = package_dir / "routes"
            self.routes_package = f"{package}.routes"
            self.static_dir = package_dir / "static"
        elif name == "route_view_class":
            view_class = value
            if isinstance(view_class, str):
                self.route_view_class = import_string(value)
        elif name == "current_user_serializer":
            serializer = value
            if isinstance(serializer, str):
                self.current_user_serializer = import_string(serializer)
        self.check()

    def __contains__(self, name):
        return hasattr(self, name)

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, val):
        return setattr(self, name, val)

    def check(self):
        if not (self.csr or self.ssr):
            raise ImproperlyConfigured("At least one of CSR or SSR must be enabled.")

        # Prefixes must be unique.
        if not self.admin_prefix:
            raise ImproperlyConfigured("Admin prefix must be set.")

        # Mount point & prefixes:
        # - can be an empty string
        # - must not be a single slash
        # - must not start with a slash
        # - must end with a slash
        for val, label in (
            (self.prefix, "Mount point"),
            (self.admin_prefix, "Admin prefix"),
        ):
            if not val:
                continue
            if val == "/":
                raise ImproperlyConfigured(
                    f"{label} is not valid (use an empty string instead of a slash)."
                )
            if val.startswith("/"):
                raise ImproperlyConfigured(f"{label} must not start with a slash.")
            if not val.endswith("/"):
                raise ImproperlyConfigured(f"{label} must end with a slash.")

    def as_dict(self) -> Dict[str, Any]:
        """Return a dict with *all* DjangoKit settings.

        This will include defaults plus any values set in the project's
        Django settings module in the `DJANGOKIT` dict.

        """
        return asdict(self)
