"""Base commands."""
from functools import partial

from django.conf import settings
from typer import Context, Exit

from .app import app
from .build import build_client, build_server
from .django import run_django_command
from .state import state
from .utils import (
    DEFAULT_PYTHON_VERSION,
    params,
    run,
    run_node_command,
    run_poetry_command,
)


@app.command()
def setup(python_version=DEFAULT_PYTHON_VERSION):
    """Set up project"""
    console = state.console
    console.header("Setting up project...")
    install(python_version)
    update()
    run_django_command("migrate")


@app.command()
def start(
    ctx: Context,
    csr: bool = True,
    ssr: bool = True,
    minify: bool = False,
    watch: bool = True,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
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

    if params.is_default(ctx, "csr"):
        csr = settings.DJANGOKIT.csr
    else:
        settings.DJANGOKIT.csr = csr

    if params.is_default(ctx, "ssr"):
        ssr = settings.DJANGOKIT.ssr
    else:
        settings.DJANGOKIT.ssr = ssr

    if csr:
        build_client(ssr=ssr, minify=minify, watch=watch, join=False)
    else:
        console.warning("CSR disabled")

    if ssr:
        build_server(minify=minify, watch=watch, join=False)
    else:
        console.warning("SSR disabled")

    console.header("Running Django dev server")
    reload_opt = "" if reload else "--noreload"
    run_django_command(["runserver", reload_opt, f"{host}:{port}"])


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
def check(python: bool = True, js: bool = True, exit_on_err: bool = False):
    """Check code for issues"""
    console = state.console

    if python:
        run = partial(run_poetry_command, exit_on_err=exit_on_err)

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
        run = partial(run_node_command, exit_on_err=exit_on_err)

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

        console.print()
        console.header("Removing Python lint \[ruff]...")
        run("ruff --fix .")

    if js and check_js_flag():
        run = partial(run_node_command, exit_on_err=False)

        console.print()
        console.header("Formatting JavaScript code \[eslint/prettier]...")
        result = run("eslint --fix .")
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

    # If the project has a package.json and node_modules, the --js flag
    # can be used.
    if has_node_modules():
        return True

    # Otherwise, exit with an error because it's likely that `npm i`
    # needs to be run first.
    console.error(
        "Can't format with eslint because the project doesn't contain "
        "a node_modules directory. Do you need to run `npm install`? "
    )
    raise Exit(1)
