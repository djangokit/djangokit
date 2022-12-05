# DjangoKit CLI

This package provides the DjangoKit command line interface. When it's
installed, it will install the `djangokit` console script.

To see a list of commands, run `djangokit` without any arguments (or use
the `dk` alias as shown here):

    dk

To run a Django management command:

    dk manage <args>

## Configuring the CLI

The DjangoKit CLI can be configured via `DJANGOKIT_CLI_*` environment
variables, which can be added to your project's `.env.public` file.

- `DJANGOKIT_CLI_PAGE_EXT`: Set the default page extension for page
  routes generated using `dk add-page`. This is handy if you're not 
  using TypeScript and you don't want to have to change the extension
  every time you generate a page route.
