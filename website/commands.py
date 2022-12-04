import os
import re

from djangokit.core.env import load_dotenv
from runcommands import abort, arg, command
from runcommands import commands as c
from runcommands import printer
from runcommands.commands import remote


@command
def clean(deep=False):
    """Clean up.

    This removes build, dist, and cache directories by default.

    Use the `--deep` flag to remove the virtualenv and node_modules
    directories, which shouldn't be removed in a normal cleaning.

    """
    printer.header("Cleaning...")
    c.local("rm -rf build")
    c.local("rm -rf dist")
    c.local("rm -rf src/djangokit/website/static/build")
    c.local("rm -rf __pycache__")
    c.local("find src tests -name __pycache__ -type d -exec rm -r {} \;")
    c.local("rm -rf .mypy_cache")
    if deep:
        printer.warning("Deep cleaning...")
        c.local("rm -rf .venv")
        c.local("rm -rf node_modules")


# Deployment -----------------------------------------------------------


@command
def ansible(env, host, version=None, tags=(), skip_tags=(), extra_vars=()):
    """Run ansible playbook."""
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
            ("--extra-var", f"hostname={host}"),
            ("--extra-var", f"version={version}"),
        ),
        cd=os.path.dirname(__file__),
    )


@command
def provision(env, host):
    """Provision the deployment host."""
    printer.header(f"Provisioning {host} ({env})")
    ansible(env, host, tags="provision")


@command
def upgrade_remote(env, host):
    """Upgrade the deployment host."""
    printer.header(f"Upgrading {host} ({env})")
    ansible(env, host, tags="provision-update-packages")


@command
def prepare(
    env,
    host,
    version=None,
    provision_=False,
    clean_: arg(help="Remove build directory? [no]") = False,
):
    """Prepare build locally for deployment."""
    printer.header(f"Preparing deployment to {host} ({env})")
    if clean_:
        c.local("rm -rf build")
    version = version or c.git_version()
    tags = []
    if provision_:
        tags.append("provision")
    tags.append("prepare")
    printer.hr(f"Preparing DjangoKit website version {version} for deployment")
    ansible(env, host, tags=tags, extra_vars={"version": version})


@command
def deploy(
    env: arg(help="Build/deployment environment"),
    host: arg(help="Host to deploy to"),
    version: arg(help="Name of version being deployed [short git hash]") = None,
    provision_: arg(help="Run provisioning steps? [no]") = False,
    prepare_: arg(
        short_option="-r",
        inverse_short_option="-R",
        help="Run local prep steps? [yes]",
    ) = True,
    clean_: arg(help="Remove build directory? [no]") = False,
    app: arg(help="Deploy app? [yes]") = True,
    static: arg(help="Deploy static files? [yes]") = True,
):
    """Deploy site."""
    if clean_:
        c.local("rm -rf build")

    version = version or c.git_version()
    bool_as_str = lambda b: "yes" if b else "no"

    printer.hr()
    printer.header(f"Deploying to {host} ({env})\n")
    printer.print(f"env = {env}")
    printer.print(f"host = {host}")
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
    ansible(env, host, version, tags=tags, skip_tags=skip_tags)


@command
def clean_remote(root="/sites/djangokit.org", run_as="djangokit"):
    printer.header(f"Removing old versions from {root}")

    readlink_result = remote(
        f"readlink current",
        run_as=run_as,
        cd=root,
        stdout="capture",
    )

    current_path = readlink_result.stdout.strip()

    if not current_path:
        abort(404, f"Could not read current link in {root}")

    current_version = os.path.basename(current_path)
    printer.success(f"Current version: {current_version}")

    find_result = remote(
        f"find {root} -mindepth 1 -maxdepth 1 -type d -not -name '.*' -not -name 'pip'",
        run_as=run_as,
        stdout="capture",
    )

    paths = find_result.stdout_lines
    paths = [p for p in paths if re.fullmatch(r"[0-9a-f]{12}", os.path.basename(p))]

    if not paths:
        abort(404, f"No versions found in {root}")

    try:
        paths.remove(current_path)
    except ValueError:
        paths = "\n".join(paths)
        abort(404, f"Current version not found in paths:\n{paths}")

    if not paths:
        abort(0, f"No versions other than current found", color="warning")

    for path in paths:
        version = os.path.basename(path)

        du_result = remote(f"du -sh {path} | awk '{{ print $1 }}'", stdout="capture")
        size = du_result.stdout.strip()

        printer.warning(f"Removing version: {version} ({size})... ", end="")
        remote(f"rm -r {path}", run_as=run_as)
        printer.success("Done")
