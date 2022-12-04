"""Base commands."""
from pathlib import Path

from djangokit.core.env import getenv
from typer import Abort, Context, Exit, Option

from .app import app, state
from .build import build_client, build_server
from .django import run_django_command
from .utils import params, run, run_node_command, run_poetry_command


@app.command()
def setup(python_version=None):
    """Set up project"""
    console = state.console
    console.header(f"Setting up project...")
    install(python_version)
    update()
    run_django_command("migrate")


@app.command()
def start(
    ssr: bool = Option(True, envvar="DJANGOKIT_SSR"),
    minify: bool = False,
    watch: bool = True,
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
    if ssr:
        build_server(minify=minify, watch=watch, join=False)
    build_client(ssr=ssr, minify=minify, watch=watch, join=False)
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
def check(
    ctx: Context,
    python: bool = True,
    js: bool = Option(True, envvar="DJANGOKIT_CLI_HAS_NODE_MODULES"),
):
    """Check code for issues"""
    console = state.console

    if python:
        console.header("Checking Python formatting \[black]...")
        run_poetry_command("black --check .")

        console.header(f"Checking Python imports \[isort]...")
        run_poetry_command("isort --check --profile black .")

        console.header(f"Checking Python types \[mypy]...")
        run_poetry_command("mypy")

    if js and check_has_node_modules(ctx):
        console.header(f"Checking JavaScript formatting \[eslint/prettier]...")

        result = run_node_command("eslint .")
        if result.returncode == 0:
            console.success("No issues found")

        console.header(f"Checking JavaScript types \[tsc]...")
        result = run("tsc --project tsconfig.json")
        if result.returncode == 0:
            console.success("No issues found")


@app.command(name="format")
def format_(
    ctx: Context,
    python: bool = True,
    js: bool = Option(True, envvar="DJANGOKIT_CLI_HAS_NODE_MODULES"),
):
    """Format code"""
    console = state.console

    if python:
        console.header(f"Formatting Python code \[black]...")
        run_poetry_command("black .")

        console.header(f"Sorting Python imports \[isort]...")
        run_poetry_command("isort --profile black .")

    if js and check_has_node_modules(ctx):
        console.header(f"Formatting JavaScript code \[eslint/prettier]...")
        result = run_node_command("eslint --fix .")
        if result.returncode == 0:
            console.success("No issues found")


def check_has_node_modules(ctx: Context):
    console = state.console
    node_modules_exists = Path("./node_modules").exists()

    if node_modules_exists:
        return True

    if params.is_default(ctx, "js"):
        console.warning(
            "Skipping eslint formatting because CWD doesn't "
            "contain a node_modules directory. Run `npm install` "
            "or use the --no-js flag to avoid this warning. "
            f"CWD = {state.cwd}"
        )
        return False

    # Explicit --js is an error
    console.error(
        "Can't format with eslint because CWD doesn't contain a "
        "node_modules directory. Do you need to run `npm install`? "
        f"CWD = {state.cwd}"
    )
    raise Exit(1)
