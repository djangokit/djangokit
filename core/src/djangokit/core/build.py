import subprocess
from pathlib import Path

from django.template.loader import render_to_string

from .conf import settings
from .exceptions import BuildError


def build(minify=False, request=None) -> Path:
    """Build React app bundle for client.

    Steps:

    - Get route info
    - Generate entrypoint file with routes
    - Run esbuild on entrypoint file, creating a bundle
    - Return path to bundle

    .. note::
        In production, this only needs to be run once and the result can
        be cached until the next deployment. In development, the result
        can be cached until a layout or page component is added or
        updated.

    """
    from .routes import get_route_info  # noqa: avoid circular import

    template = "djangokit/main.client.jsx"
    build_dir = settings.static_build_dir
    build_path = build_dir / "main.client.jsx"
    bundle_path = build_dir / "bundle.client.js"

    if not build_dir.exists():
        build_dir.mkdir()

    # Create entrypoint with routes ------------------------------------

    context = {"routes": get_route_info(settings.routes_dir)}
    client_script = render_to_string(template, context, request)
    with build_path.open("w") as fp:
        fp.write(client_script)

    # Create client bundle from entrypoint -----------------------------

    args = [
        "npx",
        "esbuild",
        "--bundle",
        build_path,
        f"--outfile={bundle_path}",
    ]
    if minify:
        args.append("--minify")
    result = subprocess.run(args)
    if result.returncode:
        raise BuildError(f"Could not build client bundle from {build_path}")

    return build_path
