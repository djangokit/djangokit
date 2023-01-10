from cookiecutter.main import cookiecutter
from typer import Argument, Option

from ..app import app
from ..utils import DEFAULT_PYTHON_VERSION


@app.command()
def create_project(
    project_name: str = Argument(..., help="Project name (e.g. 'My Project')"),
    package_name: str = Option(None, help="Package name (e.g., 'my_project')"),
    dist_name: str = Option(
        None,
        help="Distribution name (often the same as package name, but not always)",
    ),
    description: str = Option(None, help="Description"),
    version: str = Option(None, "-v", "--version", help="Initial version"),
    author: str = Option(None, help="Author name"),
    author_email: str = Option(None, help="Author email"),
    python_version: str = Option(DEFAULT_PYTHON_VERSION, help="Python version"),
    license: str = Option(None, help="Short license name (e.g., 'MIT' or 'GPL-3.0')"),
):
    """Create a new DjangoKit project

    Only the project name is required. Any options that aren't passed
    will be prompted for on the command line. The default prompt values
    for package name, dist name, and description will be derived from
    the project name (e.g., "My Project" -> "my_project").

    See https://opensource.org/licenses/alphabetical for a list of
    license names/identifiers.

    """
    extra_context = {
        "project_name": project_name,
        "package_name": package_name,
        "dist_name": dist_name or package_name,
        "description": description,
        "version": version,
        "author": author,
        "author_email": author_email,
        "python_version": python_version,
        "license": license,
    }
    extra_context = {n: v for n, v in extra_context.items() if v is not None}
    cookiecutter(
        "https://github.com/djangokit/djangokit",
        directory="cookiecutter",
        extra_context=extra_context,
    )
