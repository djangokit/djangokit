"""DjangoKit CLI entry point."""
from . import django  # noqa: Needed to register Django commands
from .app import app, state


@app.callback(no_args_is_help=True)
def main(env: str = "dev"):
    """DjangoKit CLI

    Commands must be run from the top level directory of your project.

    """
    state["env"] = env


if __name__ == "__main__":
    app()
