import shlex
import subprocess
from typing import List, Union

from rich import print

Arg = Union[str, List[str]]
Args = List[Arg]


def run(args: Args, quiet=False) -> subprocess.CompletedProcess:
    """Run a command in a subprocess.

    .. note::
        In many cases, it's better to use :func:`run_poetry_command`
        to ensure the command is run in the project's virtualenv.

    """
    args = process_args(args)
    return subprocess_run(args, quiet)


def run_node_command(args: Args, quiet=False) -> subprocess.CompletedProcess:
    """Run a command via npx in a subprocess.

    This is a convenience for `npx <args>`.

    """
    args = ["npx"] + process_args(args)
    return subprocess_run(args, quiet)


def run_poetry_command(args: Args, quiet=False) -> subprocess.CompletedProcess:
    """Run a command via poetry in a subprocess.

    This is a convenience for `poetry run <args>`.

    """
    args = ["poetry", "run"] + process_args(args)
    return subprocess_run(args, quiet)



def subprocess_run(args: List[str], quiet=False) -> subprocess.CompletedProcess:
    if not quiet:
        print(f"[bold]> {' '.join(args)}")
    return subprocess.run(args)


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


def flatten_args(args: List) -> List[str]:
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
