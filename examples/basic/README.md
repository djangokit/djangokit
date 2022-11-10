# Basic DjangoKit Example

## Prerequisites

Before proceeding, you'll need to install the `poetry` package.

> TIP: [pipx](https://pypa.github.io/pipx/) is a good way to install
> command line tools like `poetry`.

If you're on a Mac and using Homebrew, you can run the following
commands:

    brew install pipx
    pipx install poetry

Other options for installing `poetry` can be found in its docs:

- https://python-poetry.org/docs/#installation

## Install and Run Your Project

Change into the project directory and install the package:

    poetry env use ^3.11
    poetry install

Complete the installation process:

    # NOTE: You might need to activate the virtualenv created by Poetry
    #       in order to pick up the `dk` command.
    dk install

Run the dev server:

    dk start
