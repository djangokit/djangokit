# {{ cookiecutter.project_name }}

## Prerequisites

- Install the version of Python you want to use. Versions 3.8 and up are
  supported.

- Install the version of Node.js you want to use. Versions 16 and up are
  supported.

- Install `poetry`.

  > TIP: [pipx](https://pypa.github.io/pipx/) is a good way to install
  > command line tools like `poetry`.

  If you're on a Mac and using Homebrew, you can run the following
  commands:

      brew install pipx
      pipx install poetry

  Other options for installing `poetry` can be found in its docs:
  https://python-poetry.org/docs/#installation

## Install and Run Your Project

Change into the project directory and install the package:

    poetry env use {{ cookiecutter.python_version }}
    poetry install

Complete the installation process:

    # NOTE: You might need to activate the virtualenv created by Poetry
    #       in order to pick up the `dk` command.
    dk install

Run the dev server:

    dk start
