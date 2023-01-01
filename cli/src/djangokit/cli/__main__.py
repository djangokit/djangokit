"""DjangoKit console script entry point."""
from importlib import import_module
from pathlib import Path
from typing import Any

import typer

from .app import app as typer_app
from .django import manage

# Import all module to register commands
root = Path(__file__).parent
files = root.glob("**/*.py")
for file in files:
    module_name = file.stem
    if module_name.startswith("_"):
        continue
    rel_path = file.relative_to(root)
    module_path = rel_path.parent / module_name
    import_path = module_path.as_posix()
    import_path = import_path.replace("/", ".")
    import_path = f".{import_path}"
    import_module(import_path, package="djangokit.cli")


app: Any = typer.main.get_command(typer_app)
app.add_command(manage, "manage")

if __name__ == "__main__":
    app()
