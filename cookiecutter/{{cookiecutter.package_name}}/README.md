# {{ cookiecutter.project_name }}

## Prerequisites

- Install the version of Python you want to use. Versions 3.8 and up are
  supported.

- Install the version of Node.js you want to use. Versions 16 and up are
  supported.

- Install `uv`.

  If you're on a Mac and using Homebrew, you can run the following
  commands:

      brew install uv

  Other options for installing `uv` can be found in its docs:

  https://docs.astral.sh/uv/getting-started/installation/

## Install and Run Your Project

Change into the project directory and install the package:

    uv sync

Complete the installation process:

    uv run dk install

Run the dev server:

    uv run dk start
