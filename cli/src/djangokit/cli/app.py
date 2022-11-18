"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
from dataclasses import dataclass, field

import typer

from .utils.project import Config, read_project_config

app = typer.Typer()


@dataclass
class State:
    """DjangoKit CLI global app state"""

    env: str = "dev"
    quiet: bool = False
    config: Config = field(default_factory=Config)


state = State()


@app.callback(no_args_is_help=True)
def main(
    env: str = state.env,
    quiet: bool = state.quiet,
):
    """DjangoKit CLI

    Commands must be run from the top level directory of your project.

    """
    state.env = env
    state.quiet = quiet
    state.config = read_project_config(default=state.config)
