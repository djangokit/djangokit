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
    entrypoint_path = build_dir / "main.tsx"
    bundle_path = build_dir / "bundle.js"
    routes_dir = app_dir / "routes"
    routes = get_routes(routes_dir)

    if not build_dir.exists():
        build_dir.mkdir()

    # Create entrypoint ------------------------------------------------

    imports = []
    for layout_info in routes:
        imports.append(
            {
                "id": layout_info.id,
                "route_pattern": layout_info.route_pattern,
                "what": f"{{ default as Layout_{layout_info.id} }}",
                "path": f"../../routes/{layout_info.import_path}",
                "children": [
                    {
                        "id": page_info.id,
                        "route_pattern": page_info.route_pattern,
                        "what": f"{{ default as Page_{page_info.id} }}",
                        "path": f"../../routes/{page_info.import_path}",
                    }
                    for page_info in layout_info.children
                ],
            }
        )

    context = {
        "imports": imports,
        "routes": routes,
    }

    main_script = render_to_string("djangokit/main.tsx", context, request)
    with entrypoint_path.open("w") as fp:
        fp.write(main_script)

    # Build bundle from entrypoint -------------------------------------

    args = ["npx", "esbuild", "--bundle", entrypoint_path, f"--outfile={bundle_path}"]
    if minify:
        args.append("--minify")
    result = subprocess.run(args)
    if result.returncode:
        raise BuildError(f"Could not build main script: {entrypoint_path}")

    return BuildInfo(
        build_dir=build_dir,
        entrypoint_path=entrypoint_path,
        bundle_path=bundle_path,
    )
