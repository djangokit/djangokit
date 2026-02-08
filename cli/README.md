# DjangoKit CLI

> DjangoKit is Django + filesystem routing + TOML settings + scaffolding.
> See https://djangokit.wyattbaldwin.com/ for more information.

This package provides the DjangoKit command line interface. When it's
installed, it will install the `djangokit` console script.

To see a list of commands, run `djangokit` without any arguments or the
`dk` alias.

To run a Django management command:

    uv run dk manage <args>

## Configuring the CLI

The DjangoKit CLI can be configured via options passed to the
`djangokit` base command or settings added to your project's settings
file(s) in the `[djangokit.cli]` section. Using a settings file is
useful when you want to change a default permanently.

- `--env` / `env`: Specify the default environment to run commands in.

- `--settings-module` / `django_settings_module`: Specify the Django
  settings module.

- `--additional-settings-module` / `django_additional_settings_module`:
  Specify an *additional* Django settings module that will be loaded
  after (and override) the base settings module.

- `--settings-file` / `django_settings_file`: Path to settings file.
  This will be derived from `ENV` if not specified.

- `--quiet` / `quiet`: Squelch stdout.
