# DjangoKit CLI

This package provides the DjangoKit command line interface. When it's
installed, it will install the `djangokit` console script.

To see a list of commands, run `djangokit` without any arguments (or use
the `dk` alias as shown here):

    dk

To run a Django management command:

    dk manage <args>

> NOTE: There's a minor annoyance here that requires options for the
> Django managment command to be passed after `--` to distinguish the
> `dk` command's options from the management command's options. E.g.,
> `dk manage -- -h` or `dk manage diffsettings -- --all`.

> TODO: Fix this ^.
