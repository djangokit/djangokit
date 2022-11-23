import subprocess
from dataclasses import dataclass
from pathlib import Path

from django.apps import apps
from django.template.loader import render_to_string

from .conf import settings
from .exceptions import BuildError
from .utils import get_routes


@dataclass
class BuildInfo:
    build_dir: Path
    entrypoint_path: Path
    bundle_path: Path
    markup: str


def build(minify=False, request=None) -> BuildInfo:
    """Build front end.

    Steps:

    - Find page routes
    - Generate entrypoint file with React Router routes
    - Run esbuild on entrypoint file

    """
    package = settings.package
    app = apps.get_app_config(package)
    app_dir = Path(app.path)
    build_dir = app_dir / "static" / "build"

    client_template = "djangokit/main.client.jsx"
    client_build_path = build_dir / "main.client.jsx"
    client_bundle_path = build_dir / "bundle.client.js"

    server_template = "djangokit/main.server.jsx"
    server_build_path = build_dir / "main.server.jsx"
    server_bundle_path = build_dir / "bundle.server.js"

    routes_dir = app_dir / "routes"
    routes = get_routes(routes_dir)

    if not build_dir.exists():
        build_dir.mkdir()

    # Create client entrypoint -----------------------------------------

    context = {"routes": routes}

    client_script = render_to_string(client_template, context, request)
    with client_build_path.open("w") as fp:
        fp.write(client_script)

    server_script = render_to_string(server_template, context, request)
    with server_build_path.open("w") as fp:
        fp.write(server_script)

    # Build client bundle from entrypoint ------------------------------

    args = [
        "npx",
        "esbuild",
        "--bundle",
        client_build_path,
        f"--outfile={client_bundle_path}",
    ]
    if minify:
        args.append("--minify")
    result = subprocess.run(args)
    if result.returncode:
        raise BuildError(f"Could not build client bundle from {client_build_path}")

    # Create server entrypoint -----------------------------------------

    result = subprocess.run(
        [
            "npx",
            "esbuild",
            "--bundle",
            server_build_path,
            f"--outfile={server_bundle_path}",
        ]
    )
    if result.returncode:
        raise BuildError(f"Could not build server bundle from {server_build_path}")

    # Generate component markup (SSR) ----------------------------------

    result = subprocess.run(["node", server_bundle_path], stdout=subprocess.PIPE)
    if result.returncode:
        raise BuildError(f"Could not run server bundle {server_bundle_path}")
    markup = result.stdout.decode("utf-8").strip()

    return BuildInfo(
        build_dir=build_dir,
        entrypoint_path=client_build_path,
        bundle_path=client_bundle_path,
        markup=markup,
    )
