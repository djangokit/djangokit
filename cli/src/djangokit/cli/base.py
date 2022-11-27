"""Base commands."""
from click.core import ParameterSource
from typer import Abort, Context, Exit

from .app import app, state
from .build import build_command
from .django import run_django_command
from .utils import run, run_node_command, run_poetry_command


@app.command()
def setup(python_version=None):
    """Set up project"""
    console = state.console
    console.header(f"Setting up project...")
    install(python_version)
    update()
    run_django_command("migrate")


@app.command()
def start(watch: bool = True):
    """Run dev server & watch files"""
    console = state.console
    build_command(watch=watch, join=False)
    console.header("Running Django dev server")
    run_django_command("runserver")


@app.command()
def install(python_version=None):
    """Run `poetry install`"""
    console = state.console
    console.header(f"Installing project...")
    if python_version:
        run(f"poetry env use {python_version}")
    run("poetry install")
    run("npm install")


@app.command()
def update():
    """Run `poetry update`"""
    console = state.console
    console.header(f"Updating project...")
    run("poetry update")
    run("npm update")


@app.command()
def check(ctx: Context, python: bool = True, js: bool = True):
    """Check code for issues"""
    console = state.console

    if python:
        console.header("Checking Python formatting \[black]...")
        run_poetry_command("black --check .")

        console.header(f"Checking Python imports \[isort]...")
        run_poetry_command("isort --check --profile black .")

        console.header(f"Checking Python types \[mypy]...")
        run_poetry_command("mypy")

    if js:
        console.header(f"Checking JavaScript formatting \[eslint/prettier]...")

        if not state.has_node_modules:
            if ctx.get_parameter_source("js") == ParameterSource.DEFAULT:
                console.warning(
                    f"CWD does not appear to be a node env: {state.cwd}\n"
                    f"Skipping eslint formatting and tsc type checking.\n"
                    f"Use the --no-js flag to avoid this warning."
                )
                raise Exit()
            else:
                console.error(
                    f"CWD does not appear to be a node env: {state.cwd}\n"
                    f"Do you need to run `npm install`?"
                )
                raise Abort()

        result = run_node_command("eslint .")
        if result.returncode == 0:
            console.success("No issues found")

        console.header(f"Checking JavaScript types \[tsc]...")
        result = run("tsc --project tsconfig.json")
        if result.returncode == 0:
            console.success("No issues found")


@app.command(name="format")
def format_(ctx: Context, python: bool = True, js: bool = True):
    """Format code"""
    console = state.console

    if python:
        console.header(f"Formatting Python code \[black]...")
        run_poetry_command("black .")

        console.header(f"Sorting Python imports \[isort]...")
        run_poetry_command("isort --profile black .")

    if js:
        console.header(f"Formatting JavaScript code \[eslint/prettier]...")

        if not state.has_node_modules:
            if ctx.get_parameter_source("js") == ParameterSource.DEFAULT:
                console.warning(
                    f"CWD does not appear to be a node env: {state.cwd}\n"
                    f"Skipping eslint formatting.\n"
                    f"Use the --no-js flag to avoid this warning."
                )
                raise Exit()
            else:
                console.error(
                    f"CWD does not appear to be a node env: {state.cwd}\n"
                    f"Do you need to run `npm install`?"
                )
                raise Abort()

        result = run_node_command("eslint --fix .")
        if result.returncode == 0:
            console.success("No issues found")
