"""DjangoKit console script entry point."""
import typer

# NOTE: These imports are needed to register the commands in each
#       module.
from . import base  # noqa
from . import build  # noqa
from . import django  # noqa
from . import routes  # noqa
from .app import app

app = typer.main.get_command(app)
app.add_command(django.manage, "manage")

if __name__ == "__main__":
    app()
