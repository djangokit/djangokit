# DjangoKit Cookiecutter

This `cookiecutter` template can be used to create a DjangoKit app. This
is similar to running `django-admin startproject`, but more setup is
done for you up front (and the setup is somewhat opinionated).

## Using the DjangoKit CLI

Rather than using this `cookiecutter` directly, you can install the
DjangoKit CLI and run `dk -s create-project <name>`:

```shell
# Install DjangoKit CLI using pipx:
pipx install org-djangokit-cli

# Or you can use pip:
pip install --user org-djangokit-cli

# NOTE: Make sure to include the -s (standalone) flag.
dk -s create-project <name>
```

Follow the prompts and then see the README file in your newly-created
project for information on how to install and run it.

## Prerequisites

- Install the version of Python you want to use. Versions 3.9 and up are
  supported.
 
- Install `cookiecutter`.

  > TIP: [pipx](https://pypa.github.io/pipx/) is a good way to install
  > command line tools like `cookiecutter`.

  If you're on a Mac and using Homebrew, you can install `pipx` with
  `brew`:

      brew install pipx

  After installing `pipx`:
 
      pipx install cookiecutter

  You can also use `pip`:

      pip install --user cookiecutter

  Other options for installing `cookiecutter` can be found in their
  respective docs:

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
