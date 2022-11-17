"""DjangoKit console script entry point."""
# NOTE: These imports are needed to register the commands in each
#       module.
from . import base  # noqa
from . import build  # noqa
from . import django  # noqa
from .app import app

if __name__ == "__main__":
    app()
