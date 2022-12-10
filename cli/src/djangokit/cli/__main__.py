"""DjangoKit console script entry point."""
from typing import Any

import typer

# NOTE: These imports are needed to register the commands in each
#       module.
from . import base  # noqa
from . import build  # noqa
from . import django  # noqa
from .app import app
from .scaffolding import routes  # noqa

# XXX: Any
app: Any = typer.main.get_command(app)
app.add_command(django.manage, "manage")

if __name__ == "__main__":
    app()
