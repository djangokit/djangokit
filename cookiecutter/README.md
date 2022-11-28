# DjangoKit Cookiecutter

This cookiecutter template can be used to create a DjangoKit app. This
is similar to running `django-admin startproject`, but more setup is
done for you up front (and the setup is somewhat opinionated).

## Prerequisites

- Install the version of Python you want to use. Versions 3.8 and up are
  supported.
 
- Install `poetry` and `cookiecutter`.

  > TIP: [pipx](https://pypa.github.io/pipx/) is a good way to install
  > command line tools like `poetry` and `cookiecutter`.

  If you're on a Mac and using Homebrew, you can run the following
  commands:

      brew install pipx
      pipx install poetry
      pipx install cookiecutter

  Other options for installing these packages can be found in their
  respective docs:

  - https://python-poetry.org/docs/#installation
  - https://cookiecutter.readthedocs.io/en/stable/installation.html

## Create Your DjangoKit-based Project

Run the following command:

    cookiecutter https://github.com/djangokit/djangokit --directory cookiecutter

> NOTE: The `--directory` option is _required_.

Enter your project data when prompted. For example:

    project_name [DjangoKit Project]: Todos
    dist_name [todos]: <Enter>
    package_name [todos]: <Enter>
    description [Todos]: <Enter>
    ...

## Install and Run Your Project

See the README file in your newly-created project for information on how
to install and run it.
