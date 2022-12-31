# Changelog for DjangoKit Core

## 0.0.3 - unreleased

In progress...

## 0.0.2 - 2022-12-31

Second alpha prerelease.

Highlights:

- Switched from dotenv files to TOML settings files for env-specific
  settings (individual settings can still be configured to be loaded
  from env vars if needed).
- Changed routing so that the page and handlers for a given route are
  all served from the same URL (i.e., handlers are no longer served from
  `<route>/$api`).
- Added subpath handlers for routes.
- Added option to allow route URL patterns with file name extensions.
- Started adding loader functionality. This isn't fully implemented and
  loaders are not currently being used.
- Fixed a server side rendering bug where the server side markup was
  being generated twice per page (i.e., calling out to `node` twice per
  page and redundantly generating the SSR markup).
- Added cache settings and basic/default cache handling.
- Added more settings for better configurability.
- Added more tests.

All changes since 0.0.1 can be viewed by running:

    git log --oneline --reverse core-v0.0.1.. -- core

## 0.0.1 - 2022-12-13

Initial version
