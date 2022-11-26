import shutil
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

    build_dir = settings.static_build_dir
    main_path = build_dir / "main.client.jsx"
    bundle_path = build_dir / "bundle.client.js"

    if build_dir.exists():
        shutil.rmtree(build_dir)

    build_dir.mkdir()

    # Create entrypoint with routes ------------------------------------

    module_templates = (
        "djangokit/context.jsx",
        "djangokit/routes.jsx",
        "djangokit/client-app.jsx",
        "djangokit/main.client.jsx",
    )

    context = {"routes": get_route_info(settings.routes_dir)}

    for template in module_templates:
        path = build_dir / Path(template).name
        content = render_to_string(template, context, request)
        with path.open("w") as fp:
            fp.write(content)

    # Create client bundle from entrypoint -----------------------------

    args = [
        "npx",
        "esbuild",
        main_path,
        "--bundle",
        f"--inject:{build_dir / 'context.jsx'}",
        f"--outfile={bundle_path}",
    ]
    if minify:
        args.append("--minify")
    result = subprocess.run(args)
    if result.returncode:
        raise BuildError(f"Could not build client bundle from {main_path}")

    return main_path
