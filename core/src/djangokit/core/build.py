import subprocess
from pathlib import Path
from typing import List, Optional

from django.http import HttpRequest
from django.template.loader import get_template

from .conf import settings
from .exceptions import BuildError, RenderError


def make_client_bundle(
    env=None,
    minify=False,
    source_map=False,
    quiet=None,
    chdir: Optional[Path] = None,
) -> Path:
    """Build React app bundle for client.

    .. note::
        In production, this only needs to be run once and the result can
        be cached until the next deployment. In development, the result
        can be cached until a layout or page component is added or
        updated.

    """
    return make_bundle(
        "client.main.jsx",
        "client.bundle.js",
        [
            "djangokit/context.jsx",
            "djangokit/routes.jsx",
            "djangokit/client.app.jsx",
            "djangokit/client.main.jsx",
        ],
        env=env,
        minify=minify,
        source_map=source_map,
        quiet=quiet,
        chdir=chdir,
    )


def make_server_bundle(
    request: HttpRequest,
    env=None,
    minify=False,
    source_map=False,
    quiet=None,
    chdir: Optional[Path] = None,
) -> str:
    """Build React app bundle for server side rendering."""
    return make_bundle(
        "server.main.jsx",
        "server.bundle.js",
        [
            "djangokit/context.jsx",
            "djangokit/routes.jsx",
            "djangokit/server.app.jsx",
            "djangokit/server.main.jsx",
        ],
        env=env,
        minify=minify,
        source_map=source_map,
        quiet=quiet,
        request=request,
        chdir=chdir,
    )


def make_bundle(
    entrypoint_name: str,
    bundle_name: str,
    module_names: List[str],
    *,
    env=None,
    minify=True,
    source_map=False,
    quiet=None,
    request: Optional[HttpRequest] = None,
    chdir: Optional[Path] = None,
) -> Path:
    """Run esbuild to create a bundle.

    Returns the build path of the bundle.

    """
    from .routes import make_route_dir_tree  # noqa: avoid circular import

    debug = settings.DEBUG

    if env is None:
        env = "development" if debug else "production"

    if quiet is None:
        quiet = env == "production"

    build_dir = settings.static_build_dir
    entrypoint_path = build_dir / entrypoint_name
    bundle_path = build_dir / bundle_name

    build_dir.mkdir(exist_ok=True)

    # Create entrypoint with routes ------------------------------------

    templates = tuple(
        (
            get_template(name),  # Template object
            build_dir / Path(name).name,  # Build path for template
        )
        for name in module_names
    )

    tree = make_route_dir_tree()

    context = {
        "env": env,
        "routes": {
            "imports": tree.js_imports("../../routes"),
            "routes": tree.js_routes(),
        },
        "settings": settings,
    }

    for template, build_path in templates:
        content = template.render(context, request)
        with build_path.open("w") as fp:
            fp.write(content)

    # Create bundle from entrypoint ------------------------------------

    args = [
        "npx",
        "esbuild",
        entrypoint_path,
        "--bundle",
        f"--define:DEBUG={str(debug).lower()}",
        f"--define:ENV='{env}'",
        f"--inject:{build_dir / 'context.jsx'}",
        f"--outfile={bundle_path}",
    ]

    if minify:
        args.append("--minify")
    if source_map:
        args.append("--sourcemap")
    if quiet:
        args.append("--log-level=error")

    result = subprocess.run(args, cwd=chdir)

    if result.returncode:
        raise BuildError(f"Could not build bundle from {entrypoint_path}")

    return bundle_path


def run_bundle(
    bundle: Path,
    argv: List[str] = (),
    *,
    chdir: Optional[Path] = None,
) -> str:
    """Run a bundle as a Node script and capture its output.

    Used mainly for server side rendering.

    """
    args = ["node", bundle]
    if argv:
        args.extend(argv)
    result = subprocess.run(args, stdout=subprocess.PIPE, cwd=chdir)
    if result.returncode:
        raise RenderError(f"Could not run server bundle {bundle}")
    markup = result.stdout.decode("utf-8").strip()
    return markup
