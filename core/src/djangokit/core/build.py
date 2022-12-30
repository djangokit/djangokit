import json
import subprocess
from pathlib import Path
from typing import List, Optional

from django.conf import settings
from django.http import HttpRequest
from django.template.loader import select_template

from .conf import load_settings
from .exceptions import BuildError, RenderError


def make_client_bundle(
    env=None,
    settings_file=None,
    minify=False,
    source_map=True,
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
        "client.main",
        "client.bundle.js",
        [
            "context",
            "routes",
            "wrapper",
            "client.auth",
            "client.wrapper",
            "client.app",
        ],
        env=env,
        settings_file=settings_file,
        minify=minify,
        source_map=source_map,
        quiet=quiet,
        chdir=chdir,
    )


def make_server_bundle(
    request: HttpRequest,
    env=None,
    settings_file=None,
    minify=False,
    source_map=False,
    quiet=None,
    chdir: Optional[Path] = None,
) -> Path:
    """Build React app bundle for server side rendering."""
    return make_bundle(
        "server.main",
        "server.bundle.js",
        [
            "context",
            "routes",
            "wrapper",
            "server.auth",
            "server.wrapper",
            "server.app",
        ],
        env=env,
        settings_file=settings_file,
        minify=minify,
        source_map=source_map,
        quiet=quiet,
        request=request,
        chdir=chdir,
    )


def make_bundle(
    entrypoint_name: str,
    bundle_name: str,
    template_names: List[str],
    *,
    env=None,
    settings_file=None,
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

    loaded_settings = load_settings(path=settings_file, env=env)

    # React app templates are rendered into <package>/app/build
    build_dir = settings.DJANGOKIT.app_dir / "build"
    build_dir.mkdir(exist_ok=True)

    # Path to React entrypoint that's fed to esbuild.
    entrypoint_path = build_dir / entrypoint_name

    # Bundles are built into <package>/static/build
    bundle_dir = settings.DJANGOKIT.static_dir / "build"
    bundle_dir.mkdir(exist_ok=True)

    # Path to bundle that's output from esbuild.
    bundle_path = bundle_dir / bundle_name

    # Create entrypoint with routes ------------------------------------

    templates = [get_template(entrypoint_name)]
    templates.extend(get_template(name) for name in template_names)
    tree = make_route_dir_tree()
    context = {
        "env": env,
        "routes": {
            "imports": tree.js_imports("../../routes"),
            "routes": tree.js_routes(),
        },
        "settings": settings.DJANGOKIT,
    }

    for template in templates:
        content = template.render(context, request)
        template_path = Path(template.origin.name)
        build_path = build_dir / template_path.name
        with build_path.open("w") as fp:
            fp.write(content)

    # Create bundle from entrypoint ------------------------------------

    args = [
        "npx",
        "esbuild",
        str(entrypoint_path),
        "--bundle",
        f"--inject:{build_dir / 'context.jsx'}",
        f"--outfile={bundle_path}",
        f"--define:DEBUG={json.dumps(debug)}",
        f"--define:ENV={json.dumps(env)}",
    ]

    # Inject settings from file.
    for name, val in loaded_settings.items():
        if name in ("django", "djangokit"):
            continue
        name = name.upper()
        args.append(f"--define:{name}={json.dumps(val)}")

    for name, val in loaded_settings.get("django", {}).items():
        name = f"DJANGO_{name.upper()}"
        args.append(f"--define:{name}={json.dumps(val)}")

    for name, val in loaded_settings.get("djangokit", {}).items():
        name = f"DJANGOKIT_{name.upper()}"
        args.append(f"--define:{name}={json.dumps(val)}")

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


def get_template(name, extensions=("tsx", "jsx")):
    candidates = [f"{name}.{ext}" for ext in extensions]
    return select_template(candidates)


def run_bundle(bundle: Path, argv: List[str], *, chdir: Optional[Path] = None) -> str:
    """Run a bundle as a Node script and capture its output.

    Used mainly for server side rendering.

    """
    args = ["node", str(bundle)]
    if argv:
        args.extend(argv)
    result = subprocess.run(args, stdout=subprocess.PIPE, cwd=chdir)
    if result.returncode:
        raise RenderError(f"Could not run server bundle {bundle}")
    markup = result.stdout.decode("utf-8").strip()
    return markup
