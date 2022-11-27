import subprocess
from pathlib import Path
from typing import List, Optional

from django.conf import settings as django_settings
from django.http import HttpRequest
from django.template.loader import get_template

from .conf import settings
from .exceptions import BuildError, RenderError


def make_client_bundle(env=None, minify=True, quiet=None) -> Path:
    """Build React app bundle for client.

    .. note::
        In production, this only needs to be run once and the result can
        be cached until the next deployment. In development, the result
        can be cached until a layout or page component is added or
        updated.

    """
    return make_bundle(
        "main.client.jsx",
        "bundle.client.js",
        [
            "djangokit/context.jsx",
            "djangokit/routes.jsx",
            "djangokit/client-app.jsx",
            "djangokit/main.client.jsx",
        ],
        env=env,
        minify=minify,
        quiet=quiet,
    )


def make_server_bundle(
    request: HttpRequest,
    env=None,
    minify=False,
    quiet=None,
) -> str:
    """Build React app bundle for server side rendering."""
    return make_bundle(
        "main.server.jsx",
        "bundle.server.js",
        [
            "djangokit/context.jsx",
            "djangokit/routes.jsx",
            "djangokit/server-app.jsx",
            "djangokit/main.server.jsx",
        ],
        env=env,
        minify=minify,
        quiet=quiet,
        request=request,
    )


def render_bundle(bundle_path: Path) -> str:
    """Run a bundle as a Node script and capture its output.

    Used mainly for server side rendering.

    """
    result = subprocess.run(["node", bundle_path], stdout=subprocess.PIPE)
    if result.returncode:
        raise RenderError(f"Could not run server bundle {bundle_path}")
    markup = result.stdout.decode("utf-8").strip()
    return markup


def make_bundle(
    entrypoint_name: str,
    bundle_name: str,
    module_names: List[str],
    *,
    env=None,
    minify=True,
    quiet=None,
    request: Optional[HttpRequest] = None,
) -> Path:
    """Run esbuild to create a bundle.

    Returns the build path of the bundle.

    """
    from .routes import get_route_info  # noqa: avoid circular import

    if env is None:
        env = "development" if django_settings.DEBUG else "production"

    if quiet is None:
        quiet = env == "production"

    build_dir = settings.static_build_dir
    entrypoint_path = build_dir / entrypoint_name
    bundle_path = build_dir / bundle_name

    build_dir.mkdir(exist_ok=True)
    bundle_path.unlink(missing_ok=True)

    # Create entrypoint with routes ------------------------------------

    templates = tuple(
        (
            get_template(name),  # Template object
            build_dir / Path(name).name,  # Build path for template
        )
        for name in module_names
    )

    for _, build_path in templates:
        build_path.unlink(missing_ok=True)

    context = {
        "env": env,
        "routes": get_route_info(settings.routes_dir),
    }

    for template, build_path in templates:
        content = template.render(context, request)
        with build_path.open("w") as fp:
            fp.write(content)

    # Create client bundle from entrypoint -----------------------------

    args = [
        "npx",
        "esbuild",
        entrypoint_path,
        "--bundle",
        "--sourcemap",
        f"--inject:{build_dir / 'context.jsx'}",
        f"--outfile={bundle_path}",
    ]
    if minify:
        args.append("--minify")
    if quiet:
        args.append("--log-level=error")
    result = subprocess.run(args)
    if result.returncode:
        raise BuildError(f"Could not build bundle from {entrypoint_path}")

    return bundle_path
