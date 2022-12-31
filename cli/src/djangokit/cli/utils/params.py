from functools import lru_cache
from typing import Any, Callable

from click.core import ParameterSource
from typer import BadParameter, CallbackParam, Context


def is_default(ctx: Context, name: str) -> bool:
    """Did the param value come from the default source?"""
    if name not in ctx.params:
        raise KeyError(f"Unknown parameter for command {ctx.command.name}: {name}")
    source = ctx.get_parameter_source(name)
    return source == ParameterSource.DEFAULT


def is_env(ctx: Context, name: str) -> bool:
    """Did the param value come from an env var?"""
    if name not in ctx.params:
        raise KeyError(f"Unknown parameter for command {ctx.command.name}: {name}")
    source = ctx.get_parameter_source(name)
    return source == ParameterSource.ENVIRONMENT


@lru_cache(maxsize=None)
def exclusive(group_name: str) -> Callable[[Context, CallbackParam, Any], Any]:
    """Use to create mutually exclusive options.

    .. note::
        The use of an LRU cache is to ensure the same callback is always
        returned for a given mutual exclusion group. To ensure isolation
        between commands, use a name like `<command name>:<group name>`.

    Example::

        @app.command()
        def do_stuff(
            with_thing: bool = Option(
                False,
                callback=exclusive("do-stuff:thing"),
            ),
            with_other_thing: bool = Option(
                False,
                callback=exclusive("do-stuff:thing"),
            ),
        ):
            if with_thing:
                ...
            elif with_other_thing:
                ...

    """
    # This will be populated with params in the group that were
    # explicitly provided.
    explicit_group_params = []

    def callback(ctx: Context, param: CallbackParam, value: Any) -> Any:
        name = param.name

        if name is not None:
            source = ctx.get_parameter_source(name)
        else:
            return value

        if source == ParameterSource.DEFAULT:
            return value

        explicit_group_params.append(param)

        if len(explicit_group_params) > 1:
            first_param: CallbackParam = explicit_group_params[0]
            opt_name = sorted(first_param.opts, key=lambda opt: len(opt))[-1]
            raise BadParameter(
                f"mutually exclusive with {opt_name} "
                f"(mutual exclusion group: {group_name})"
            )

        return value

    return callback
