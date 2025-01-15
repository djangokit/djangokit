# DjangoKit Website

## Prerequisites

Before proceeding, you'll need to install `uv`.

If you're on a Mac and using Homebrew, you can run the following
commands:

    brew install uv

Other options for installing `uv` can be found in its docs:

https://docs.astral.sh/uv/getting-started/installation/

## Create Development Settings File

Create `settings.development.toml` with the following content:

```
[django]
DEBUG = true
SECRET_KEY = "change this to a random value"
```

**NOTE**: This file is git-ignored.

## Install

Change into the project directory and install the package:

    uv sync

## Run Database Migrations

    uv run dk migrate

## Run

Complete the installation process:

    uv run dk install

Run the dev server:

    uv run dk start
