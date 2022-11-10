import shlex
import subprocess
from typing import List, Union

import typer

Arg = Union[str, List[str]]
Args = Union[Arg, List[Arg]]


def run(args: Args, exit_on_err=True) -> subprocess.CompletedProcess:
    """Run a command in a subprocess.

    .. note::
        In many cases, it's better to use :func:`run_poetry_command` or
        :func:`run_poetry_command` to ensure the command is run in the
        project's node env or virtualenv.

    """
    args = process_args(args)
    return subprocess_run(args, exit_on_err)


def run_node_command(args: Args, exit_on_err=True) -> subprocess.CompletedProcess:
    """Run a command via npx in a subprocess.

    This is a convenience for `npx <args>`.

    """
    args = ["npx"] + process_args(args)
    return subprocess_run(args, exit_on_err)


def run_poetry_command(args: Args, exit_on_err=True) -> subprocess.CompletedProcess:
    """Run a command via poetry in a subprocess.

    This is a convenience for `poetry run <args>`.

    """
    args = ["poetry", "run"] + process_args(args)
    return subprocess_run(args, exit_on_err)


def subprocess_run(args: List[str], exit_on_err=True) -> subprocess.CompletedProcess:
    from ..app import state

    state.console.command(">", " ".join(args))
    result = subprocess.run(args, stdout=subprocess.DEVNULL if state.quiet else None)
    if result.returncode and exit_on_err:
        raise typer.Exit(result.returncode)
    return result


def process_args(args: Args) -> List[str]:
    """Process args before passing to `subprocess.run()`.

    If a string is passed, it will be split into a list of strings. If
    a list is passed, it will be flattened into a single list of
    strings.

    """
    if isinstance(args, str):
        args = shlex.split(args)
    else:
        args = flatten_args(args)
    return args


def flatten_args(args: Args) -> List[str]:
    """Flatten args into a single list of strings.

    If an arg is `None`, it will be removed (this is a convenience for
    flag args).

    """
    flattened = []
    for arg in args:
        if arg is None:
            continue
        elif isinstance(arg, str):
            flattened.append(arg)
        elif isinstance(arg, (list, tuple)):
            flattened.extend(flatten_args(arg))
        else:
            raise TypeError(f"Expected str, list, or tuple; got {type(arg)}")
    return flattened
