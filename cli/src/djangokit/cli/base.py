"""Base commands."""
from .app import app
from .django import run_django_command
from .utils import Console, run, run_node_command, run_poetry_command


@app.command()
def setup(python_version=None):
    """Set up project"""
    console = Console()
    console.header(f"Setting up project...")
    install(python_version)
    update()
    run_django_command("migrate")


@app.command()
def start():
    """Run dev server & watch files"""
    run_django_command("runserver")


@app.command()
def install(python_version=None):
    """Run `poetry install`"""
    console = Console()
    console.header(f"Installing project...")
    if python_version:
        run(f"poetry env use {python_version}")
    run("poetry install")
    run("npm install")


@app.command()
def update():
    """Run `poetry update`"""
    console = Console()
    console.header(f"Updating project...")
    run("poetry update")
    run("npm update")


@app.command()
def check(python: bool = True, js: bool = True):
    """Check code for issues"""
    console = Console()

    if python:
        console.header("Checking Python formatting \[black]...")
        run_poetry_command("black --check .")

        console.header(f"Checking Python imports \[isort]...")
        run_poetry_command("isort --check --profile black .")

        console.header(f"Checking Python types \[mypy]...")
        run_poetry_command("mypy")

    if js:
        console.header(f"Checking JavaScript formatting \[eslint/prettier]...")
        result = run_node_command("eslint .")
        if result.returncode == 0:
            console.success("No issues found")

        console.header(f"Checking JavaScript types \[tsc]...")
        result = run("tsc --project tsconfig.json")
        if result.returncode == 0:
            console.success("No issues found")


@app.command(name="format")
def format_(python: bool = True, js: bool = True):
    """Format code"""
    console = Console()

    if python:
        console.header(f"Formatting Python code \[black]...")
        run_poetry_command("black .")

        console.header(f"Sorting Python imports \[isort]...")
        run_poetry_command("isort --profile black .")

    if js:
        console.header(f"Formatting JavaScript code \[eslint/prettier]...")
        result = run("eslint --fix .")
        if result.returncode == 0:
            console.success("No issues found")