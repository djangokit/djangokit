"""Base commands."""
import os
from functools import partial
from pathlib import Path

from typer import Exit, Option

from .app import app, state
from .build import build_client, build_server
from .django import run_django_command
from .utils import run, run_node_command, run_poetry_command


@app.command()
def setup(python_version=None):
    """Set up project"""
    console = state.console
    console.header("Setting up project...")
    install(python_version)
    update()
    run_django_command("migrate")


@app.command()
def start(
    ssr: bool = Option(True, envvar="DJANGOKIT_SSR"),
    minify: bool = False,
    watch: bool = True,
    debug: bool = Option(
        True,
        help=(
            "Allows DEBUG mode to be easily disabled. Useful for "
            "testing Django error templates, etc."
        ),
    ),
):
    """Run dev server & watch files

    By default, pages are server-rendered (SSR) and the client bundle
    hydrates the rendered markup. The `--no-ssr` anti-flag can be used
    to disable server side rendering and enable client side-only
    rendering (CSR):

    1. The client bundle will be configured to render into the React
       root rather than hydrating it.
    2. When a page is loaded in the browser, the server side bundle and
       markup will not be generated--the page will be rendered only on
       the client.

    Disabling SSR can be useful during development because client-side
    only rendering is faster.

    """
    console = state.console
    if not debug:
        os.environ["DJANGO_DEBUG"] = "false"
        os.environ["DJANGO_ALLOWED_HOSTS"] = '["localhost"]'
    if ssr:
        build_server(minify=minify, watch=watch, join=False)
    build_client(ssr=ssr, minify=minify, watch=watch, join=False)
    console.header("Running Django dev server")
    run_django_command("runserver")


@app.command()
def install(python_version=None):
    """Run `poetry install`"""
    console = state.console
    console.header("Installing project...")
    if python_version:
        run(f"poetry env use {python_version}")
    run("poetry install")
    if has_package_json():
        console.print()
        run("npm install")


@app.command()
def update():
    """Run `poetry update`"""
    console = state.console
    console.header("Updating project...")
    run("poetry update")
    if has_package_json():
        console.print()
        run("npm update")


@app.command()
def check(python: bool = True, js: bool = True):
    """Check code for issues"""
    console = state.console

    if python:
        run = partial(run_poetry_command, exit_on_err=False)

        console.header("Checking Python formatting \[black]...")
        run("black --check .")

        console.print()
        console.header("Checking Python imports \[isort]...")
        run("isort --check --profile black .")

        console.print()
        console.header("Checking for Python lint \[ruff]...")
        run("ruff .")

        console.print()
        console.header("Checking Python types \[mypy]...")
        run("mypy")

    if js and check_js_flag():
        run = partial(run_node_command, exit_on_err=False)

        console.print()
        console.header("Checking JavaScript formatting \[eslint/prettier]...")

        result = run("eslint .")
        if result.returncode == 0:
            console.success("No issues found")

        console.print()
        console.header("Checking JavaScript types \[tsc]...")
        result = run("tsc --project tsconfig.json")
        if result.returncode == 0:
            console.success("No issues found")


@app.command(name="format")
def format_(python: bool = True, js: bool = True):
    """Format code"""
    console = state.console

    if python:
        run = partial(run_poetry_command, exit_on_err=False)

        console.header("Formatting Python code \[black]...")
        run("black .")

        console.print()
        console.header("Sorting Python imports \[isort]...")
        run("isort --profile black .")

    if js and check_js_flag():
        run = partial(run_node_command, exit_on_err=False)

        console.print()
        console.header("Formatting JavaScript code \[eslint/prettier]...")
        result = run("eslint --fix .")
        if result.returncode == 0:
            console.success("No issues found")


def has_package_json():
    return Path("./package.json").exists()


def has_node_modules():
    return Path("./node_modules").exists()


def check_js_flag():
    console = state.console

    # If the project doesn't have a package.json, the --js flag is
    # irrelevant.
    if not has_package_json():
        return False

    # If the project has a package.json and node_modules, the --js flag
    # can be used.
    if has_node_modules():
        return True

    # Otherwise, exit with an error because it's likely that `npm i`
    # needs to be run first.
    console.error(
        "Can't format with eslint because CWD doesn't contain a "
        "node_modules directory. Do you need to run `npm install`? "
        f"CWD = {state.cwd}"
    )
    raise Exit(1)
