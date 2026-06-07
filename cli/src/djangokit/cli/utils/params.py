from functools import lru_cache
from typing import Any, Callable

from typer import BadParameter, CallbackParam, Context
from typer._click.core import ParameterSource


@lru_cache
def _get_param_names(ctx: Context, command):
    params = command.get_params(ctx)
    return [param.name for param in params]


def _param_has_source(ctx: Context, param_name: str, source: ParameterSource):
    command = ctx.command
    param_names = _get_param_names(ctx, command)
    if param_name not in param_names:
        raise KeyError(f"Unknown parameter for command {command.name}: {param_name}")
    param_source = ctx.get_parameter_source(param_name)
    if param_source is None:
        return False
    return param_source == source


def has_default_value(ctx: Context, name: str) -> bool:
    """Did the param value come from the default source?"""
    return _param_has_source(ctx, name, ParameterSource.DEFAULT)


def has_env_value(ctx: Context, name: str) -> bool:
    """Did the param value come from an env var?"""
    return _param_has_source(ctx, name, ParameterSource.ENVIRONMENT)


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

        if name is None:
            raise BadParameter("mutually exclusive option unexpectedly has no name")

        if has_default_value(ctx, name):
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
