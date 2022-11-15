"""DjangoKit command line app.

This defines the CLI app. The global `app` can be imported from here and
used to add commands.

"""
import typer

app = typer.Typer()


state = {
    "env": "dev",
    "quiet": False,
}


@app.callback(no_args_is_help=True)
def main(
    env: str = state["env"],
    quiet: bool = state["quiet"],
):
    """DjangoKit CLI

    Commands must be run from the top level directory of your project.

    """
    state["env"] = env
    state["quiet"] = quiet
