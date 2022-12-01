import os

from djangokit.core.env import load_dotenv
from runcommands import command
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
    env,
    hostname,
    version=None,
    provision_=False,
    prepare_=True,
    app=True,
    static=True,
):
    printer.header(f"Deploying to {hostname} ({env})")
    version = version or c.git_version()
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
