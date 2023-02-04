# Changelog for DjangoKit CLI

## 0.0.8 - unreleased

In progress...

## 0.0.7 - 2023-02-04

- Fixed some issues around standalone mode.

## 0.0.6 - 2023-01-10

- Find project root in CWD or ancestors and run commands there.

## 0.0.5 - 2023-01-01

- Fixed dist config so standalone settings module is included when
  building distributions with `poetry build`.

## 0.0.4 - 2023-01-01

- Fixed an `ImportError` that would occur when running certain commands
  in standalone mode (e.g., `setup`).

## 0.0.3 - 2022-12-31

- Added `create-project` command.

## 0.0.2 - 2022-12-31

Second alpha prerelease.

Highlights:

- Switched from dotenv files to TOML settings files for env-specific
  settings (individual settings can still be configured to be loaded
  from env vars if needed).

Changes since 0.0.1 can be viewed by running:

    git log --oneline --reverse cli-v0.0.1.. -- cli

## 0.0.1 - 2022-12-13

Initial version
