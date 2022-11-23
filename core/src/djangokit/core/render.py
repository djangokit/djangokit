import subprocess

from django.http import HttpRequest
from django.template.loader import render_to_string

from .conf import settings
from .exceptions import RenderError


def render(request: HttpRequest) -> str:
    """Server side render React app based on request URL.

    Steps:

    - Get route info
    - Generate SSR script with routes
    - Run esbuild on SSR script, creating a bundle
    - Run the bundled script and capture its output
    - Return the output, which is the markup for a specific route

    .. note::
        In the current implementation, the output can be cached until
        the next deployment in production or until a layout or page
        component is added or updated in development.

        This is because page data isn't being loaded during SSR, so the
        output will always be the identical for a given page.

        If data is loaded during SSR, then caching will become more
        complex.

    """
    from .routes import get_route_info  # noqa: avoid circular import

    template = "djangokit/main.server.jsx"
    build_dir = settings.static_build_dir
    build_path = build_dir / "main.server.jsx"
    bundle_path = build_dir / "bundle.server.js"

    # Create entrypoint with routes ------------------------------------

    context = {"routes": get_route_info(settings.routes_dir)}
    server_script = render_to_string(template, context, request)
    with build_path.open("w") as fp:
        fp.write(server_script)

    # Create SSR script bundle from entrypoint -------------------------

    result = subprocess.run(
        [
            "npx",
            "esbuild",
            "--bundle",
            build_path,
            f"--outfile={bundle_path}",
        ]
    )
    if result.returncode:
        raise RenderError(f"Could not build SSR script bundle from {build_path}")

    # Run the script and capture its output ----------------------------

    result = subprocess.run(["node", bundle_path], stdout=subprocess.PIPE)
    if result.returncode:
        raise RenderError(f"Could not run server bundle {bundle_path}")
    markup = result.stdout.decode("utf-8").strip()

    return markup
