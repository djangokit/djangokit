from click.core import ParameterSource
from typer import Context


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
