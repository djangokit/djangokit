"""Base commands."""

import json
from functools import partial

from typer import Exit

from .app import app
from .django import run_django_command
from .state import state
from .utils import run, run_node_command, run_uv_command


@app.command()
def setup():
    """Set up project"""
    console = state.console
    console.header("Setting up project...")
    install()
    update()
    run_django_command("migrate")


@app.command()
def start(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Run dev server."""
    console = state.console
    console.header("Running Django dev server")
    reload_opt = "" if reload else "--noreload"
    run_django_command(["runserver", reload_opt, f"{host}:{port}"])


@app.command()
def install():
    """Install the project"""
    console = state.console
    console.header("Installing project...")
    run("uv sync")
    if has_package_json():
        console.print()
        run("npm install")


@app.command()
def update():
    """Update the project"""
    console = state.console
    console.header("Updating project...")
    run("uv sync --upgrade")
    if has_package_json():
        console.print()
        run("npm update")


@app.command()
def check(python: bool = True, js: bool = True, exit_on_err: bool = False):
    """Check code for issues

    JS checking won't be done if the package doesn't have a package.json
    file and a node_modules directory. package.json must include eslint
    as a dependency.

    """
    console = state.console

    if python:
        run_uv = partial(run_uv_command, exit_on_err=exit_on_err)

        console.header("Checking Python formatting \\[ruff]...")
        run_uv("ruff format --check .")

        console.print()
        console.header("Checking for Python lint \\[ruff]...")
        run_uv("ruff check .")

        console.print()
        console.header("Checking Python types \\[mypy]...")
        run_uv("mypy")

    if js and check_js_flag():
        run_node = partial(run_node_command, exit_on_err=exit_on_err)

        console.print()
        console.header("Checking JavaScript formatting \\[eslint/prettier]...")

        result = run_node("eslint .")
        if result.returncode == 0:
            console.success("No issues found")
        #
        # console.print()
        # console.header("Checking JavaScript types \\[tsc]...")
        # result = run_node("tsc --project tsconfig.json")
        # if result.returncode == 0:
        #     console.success("No issues found")


@app.command(name="format")
def format_(python: bool = True, js: bool = True):
    """Format code

    JS formatting won't be done if the package doesn't have a
    package.json file and a node_modules directory. package.json must
    include eslint as a dependency.

    """
    console = state.console

    if python:
        run_uv = partial(run_uv_command, exit_on_err=False)

        console.header("Formatting Python code \\[ruff]...")
        run_uv("ruff format .")

        console.print()
        console.header("Removing Python lint \\[ruff]...")
        run_uv("ruff check --fix .")

    if js and check_js_flag():
        run_node = partial(run_node_command, exit_on_err=False)

        console.print()
        console.header("Formatting JavaScript code \\[eslint/prettier]...")
        result = run_node("eslint --fix .")
        if result.returncode == 0:
            console.success("No issues found")


def has_package_json():
    return (state.project_root / "package.json").is_file()


def has_node_modules():
    return (state.project_root / "node_modules").is_dir()


def check_js_flag():
    console = state.console

    # If the project doesn't have a package.json, the --js flag is
    # irrelevant.
    if not has_package_json():
        return False

    with (state.project_root / "package.json").open("r") as fp:
        content = fp.read()
        content = json.loads(content)
        deps = content.get("dependencies")
        dev_deps = content.get("devDependencies")
        has_eslint = deps and "eslint" in deps or dev_deps and "eslint" in dev_deps
        if not has_eslint:
            console.error(
                "eslint dependency not found in package.json. "
                "eslint must be installed to format JS/TS files."
            )
            return False

    # If the project has a package.json and node_modules, the --js flag
    # can be used.
    if has_node_modules():
        return True

    # Otherwise, exit with an error because it's likely that `npm i`
    # needs to be run first.
    console.error("node_modules directory not found. Do you need to run `npm install`?")
    raise Exit(1)
