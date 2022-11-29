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
    )


@command
def provision(env, hostname):
    ansible(env, hostname, tags="provision")


@command
def upgrade_remote(env, hostname):
    ansible(env, hostname, tags="provision-update-packages")


@command
def prepare(env, hostname, version=None, provision_=False):
    version = version or c.git_version()
    tags = []
    if provision_:
        tags.append("provision")
    tags.append("prepare")
    printer.hr(f"Preparing MyStops version {version} for deployment")
    ansible(env, hostname, tags=tags, extra_vars={"version": version})


@command
def deploy(
    env,
    hostname,
    version=None,
    provision_=False,
    prepare_=True,
    backend=True,
    frontend=True,
):
    version = version or c.git_version()
    tags = []
    skip_tags = []
    if provision_:
        tags.append("provision")
    if prepare_:
        tags.append("prepare")
    if not backend:
        skip_tags.append("prepare-backend")
        skip_tags.append("deploy-backend")
    if not frontend:
        skip_tags.append("prepare-frontend")
        skip_tags.append("deploy-frontend")
    tags.append("deploy")
    printer.hr(f"Deploying MyStops version {version}")
    ansible(env, hostname, version, tags=tags, skip_tags=skip_tags)
