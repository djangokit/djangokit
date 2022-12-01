import os

from djangokit.core.env import load_dotenv
from runcommands import arg, command
from runcommands import commands as c
from runcommands import printer

# Provisioning & Deployment --------------------------------------------


@command
def ansible(env, hostname, version=None, tags=(), skip_tags=(), extra_vars=()):
    version = version or c.git_version()

    if isinstance(tags, str):
        tags = (tags,)

    if tags:
        tags = tuple(("--tag", tag) for tag in tags)
    if skip_tags:
        skip_tags = tuple(("--skip-tag", tag) for tag in skip_tags)
    if extra_vars:
        extra_vars = tuple(("--extra-var", f"{n}={v}") for (n, v) in extra_vars.items())

    load_dotenv(f".env.public")
    load_dotenv(f".env.{env}")

    c.local(
        (
            "ansible-playbook",
            "-i",
            f"ansible/{env}",
            "ansible/site.yaml",
            tags,
            skip_tags,
            extra_vars,
            ("--extra-var", f"env={env}"),
            ("--extra-var", f"hostname={hostname}"),
            ("--extra-var", f"version={version}"),
        ),
        cd=os.path.dirname(__file__),
    )


@command
def provision(env, hostname):
    printer.header(f"Provisioning {hostname} ({env})")
    ansible(env, hostname, tags="provision")


@command
def upgrade_remote(env, hostname):
    printer.header(f"Upgrading {hostname} ({env})")
    ansible(env, hostname, tags="provision-update-packages")


@command
def prepare(env, hostname, version=None, provision_=False):
    printer.header(f"Preparing deployment to {hostname} ({env})")
    version = version or c.git_version()
    tags = []
    if provision_:
        tags.append("provision")
    tags.append("prepare")
    printer.hr(f"Preparing DjangoKit website version {version} for deployment")
    ansible(env, hostname, tags=tags, extra_vars={"version": version})


@command
def deploy(
    env: arg(help="Build/deployment environment"),
    hostname: arg(help="Host to deploy to"),
    version: arg(help="Name of version being deployed [short git hash]") = None,
    provision_: arg(help="Run provisioning steps? [no]") = False,
    prepare_: arg(
        short_option="-r",
        inverse_short_option="-R",
        help="Run local prep steps? [yes]",
    ) = True,
    app: arg(help="Deploy app? [yes]") = True,
    static: arg(help="Deploy static files? [yes]") = True,
):
    """Deploy site."""
    version = version or c.git_version()

    bool_as_str = lambda b: "yes" if b else "no"

    printer.hr()
    printer.header(f"Deploying to {hostname} ({env})\n")
    printer.print(f"env = {env}")
    printer.print(f"hostname = {hostname}")
    printer.print(f"version = {version}")
    printer.print(f"provision = {bool_as_str(provision_)}")
    printer.print(f"local prep = {bool_as_str(prepare_)}")
    printer.print(f"deploy app = {bool_as_str(app)}")
    printer.print(f"deploy static = {bool_as_str(static)}")
    printer.print("")

    tags = []
    skip_tags = []
    if provision_:
        tags.append("provision")
    if prepare_:
        tags.append("prepare")
    if not app:
        skip_tags.append("prepare-app")
        skip_tags.append("deploy-app")
    if not static:
        skip_tags.append("prepare-static")
        skip_tags.append("deploy-static")
    tags.append("deploy")

    printer.hr(f"Deploying DjangoKit website version {version}")
    ansible(env, hostname, version, tags=tags, skip_tags=skip_tags)
