# DjangoKit CLI

> NOTE: DjangoKit is a full stack Django+React framework. See
> https://djangokit.org/ for more information.

This package provides the DjangoKit command line interface. When it's
installed, it will install the `djangokit` console script.

To see a list of commands, run `djangokit` without any arguments (or use
the `dk` alias as shown here):

    dk

To run a Django management command:

    dk manage <args>

## Configuring the CLI

The DjangoKit CLI can be configured via global options passed to the
`djangokit` base command or via environment variables, which can be
added to your project's `.env` file(s). Using env vars is useful when
you want to change a default permanently.

- `--env` / `ENV`: Specify the environment to run commands in.

- `--dotenv-path` / `DOTENV_PATH`: Path to `.env` file. This will be
  derived from `ENV` if not specified.

- `--settings-module` / `DJANGO_SETTINGS_MODULE`: Specify the Django
  settings module.

- `--additional_settings_module` / `DJANGO_ADDITIONAL_SETTINGS_MODULE`:
  Specify an *additional* Django settings module that will be loaded
  after (and override) the base settings module.

- `--typescript` / `DJANGOKIT_CLI_USE_TYPESCRIPT`: Since using
  TypeScript is the default, you can use this to disable TypeScript.
  This will affect how files are generated, for example (e.g. when using
  `dk add-page`).

- `--quiet` / `DJANGOKIT_CLI_QUIET`: Squelch stdout.
