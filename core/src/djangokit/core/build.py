import subprocess
from dataclasses import dataclass
from pathlib import Path

from django.apps import apps
from django.template.loader import render_to_string

from .conf import settings
from .exceptions import BuildError
from .utils import make_page_tree


@dataclass
class BuildInfo:
    build_dir: Path
    entrypoint_path: Path
    bundle_path: Path


def build(request=None) -> BuildInfo:
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
    page_info = make_page_tree(routes_dir)

    if not build_dir.exists():
        build_dir.mkdir()

    # Create entrypoint ------------------------------------------------

    imports = []
    for info in page_info:
        imports.append(
            {
                "what": f"{{ default as Page_{info.id} }}",
                "path": f"../../routes/{info.import_path}",
            }
        )

    context = {
        "imports": imports,
        "page_info": page_info,
    }

    main_script = render_to_string("djangokit/main.tsx", context, request)
    with entrypoint_path.open("w") as fp:
        fp.write(main_script)

    # Build bundle from entrypoint -------------------------------------

    result = subprocess.run(
        ["npx", "esbuild", "--bundle", entrypoint_path, f"--outfile={bundle_path}"]
    )
    if result.returncode:
        raise BuildError(f"Could not build main script: {entrypoint_path}")

    subprocess.run(["npx", "eslint", "--fix", entrypoint_path])

    return BuildInfo(
        build_dir=build_dir,
        entrypoint_path=entrypoint_path,
        bundle_path=bundle_path,
    )
