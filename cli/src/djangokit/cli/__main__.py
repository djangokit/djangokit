"""DjangoKit console script entry point."""
from typing import Any

import typer

# NOTE: These imports are needed to register the commands in each
#       module.
from . import base  # noqa
from . import build  # noqa
from . import django  # noqa
from .app import app as typer_app
from .scaffolding import routes  # noqa

app: Any = typer.main.get_command(typer_app)
app.add_command(django.manage, "manage")

if __name__ == "__main__":
    app()
