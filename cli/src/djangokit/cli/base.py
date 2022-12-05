"""Base commands."""
from pathlib import Path

from typer import Context, Exit, Option

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
    if has_package_json():
        console.print()
        run("npm install")


@app.command()
def update():
    """Run `poetry update`"""
    console = state.console
    console.header(f"Updating project...")
    run("poetry update")
    if has_package_json():
        console.print()
        run("npm update")


@app.command()
def check(python: bool = True, js: bool = True):
    """Check code for issues"""
    console = state.console

    if python:
        console.header("Checking Python formatting \[black]...")
        run_poetry_command("black --check .", exit_on_err=False)

        console.print()
        console.header(f"Checking Python imports \[isort]...")
        run_poetry_command("isort --check --profile black .", exit_on_err=False)

        console.print()
        console.header(f"Checking Python types \[mypy]...")
        run_poetry_command("mypy", exit_on_err=False)

    if js and check_js_flag():
        console.print()
        console.header(
            f"Checking JavaScript formatting \[eslint/prettier]...",
        )

        result = run_node_command("eslint .")
        if result.returncode == 0:
            console.success("No issues found")

        console.print()
        console.header(f"Checking JavaScript types \[tsc]...")
        result = run_node_command("tsc --project tsconfig.json", exit_on_err=False)
        if result.returncode == 0:
            console.success("No issues found")


@app.command(name="format")
def format_(python: bool = True, js: bool = True):
    """Format code"""
    console = state.console

    if python:
        console.header(f"Formatting Python code \[black]...")
        run_poetry_command("black .", exit_on_err=False)

        console.print()
        console.header(f"Sorting Python imports \[isort]...")
        run_poetry_command("isort --profile black .", exit_on_err=False)

    if js and check_js_flag():
        console.print()
        console.header(f"Formatting JavaScript code \[eslint/prettier]...")
        result = run_node_command("eslint --fix .", exit_on_err=False)
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
