"""DjangoKit console script entry point."""
from . import base  # noqa: Import is needed to register base commands
from . import django  # noqa: Import is needed to register Django commands
from .app import app

if __name__ == "__main__":
    app()
