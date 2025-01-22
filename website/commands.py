import datetime
import os
import posixpath
import re
import shutil
from pathlib import Path

from runcommands import abort, arg, command, confirm, printer
from runcommands import commands as c
from runcommands.commands import remote, sync  # Do not remove
from runcommands.util import flatten_args

TITLE = "DjangoKit"
SITE_USER = "djangokit"
SRC_PATH = "src/djangokit/website"
REMOTE_SITE_DIR = "/sites/djangokit"


@command
def clean(deep=False):
    """Clean up locally.

    This removes build, dist, and cache directories by default.

    Use the `--deep` flag to remove the virtualenv and node_modules
    directories, which shouldn't be removed in a normal cleaning.

    """
    printer.header("Cleaning...")

    rm_dir("build")
    rm_dir("dist")
    rm_dir(f"{SRC_PATH}/app/build")
    rm_dir(f"{SRC_PATH}/website/static/build")
    rm_dir(".mypy_cache")
    rm_dir(".pytest_cache")
    rm_dir(".ruff_cache")

    pycache_dirs = tuple(Path.cwd().glob("__pycache__"))
    if pycache_dirs:
        count = len(pycache_dirs)
        noun = "directory" if count == 1 else "directories"
        printer.info(f"removing {count} __pycache__ {noun}")
        for d in pycache_dirs:
            rm_dir(d, True)

    if deep:
        printer.warning("Deep cleaning...")
        rm_dir(".venv")
        rm_dir("node_modules")


def rm_dir(name, quiet=False):
    path = Path(name).absolute()
    rel_path = path.relative_to(path.cwd())
    if path.is_dir():
        if not quiet:
            printer.warning(f"removing directory tree: {rel_path}")
        shutil.rmtree(path)
    else:
        if not quiet:
            printer.info(f"directory not present: {rel_path}")


# Deployment -----------------------------------------------------------


@command
def ansible(
    env,
    host,
    public_hostname,
    version=None,
    tags=(),
    skip_tags=(),
    extra_vars=(),
):
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

    args = (
        "ansible-playbook",
        "-i",
        f"ansible/{env}",
        "ansible/site.yaml",
        tags,
        skip_tags,
        extra_vars,
        ("--extra-var", f"env={env}"),
        ("--extra-var", f"host={host}"),
        ("--extra-var", f"public_hostname={public_hostname}"),
        ("--extra-var", f"version={version}"),
    )

    cwd = os.path.dirname(__file__)
    cmd = " ".join(flatten_args(args))
    cmd = cmd.replace(" -", "\n  -")
    printer.header(f"Running ansible playbook with CWD = {cwd}")
    printer.print(cmd, style="bold")

    c.local(args, cd=cwd)


@command
def provision(env, host, public_hostname):
    """Provision the deployment host."""
    printer.header(f"Provisioning {public_hostname} ({env})")
    ansible(env, host, public_hostname, tags="provision")


@command
def upgrade_remote(env, host, public_hostname):
    """Upgrade the deployment host."""
    printer.header(f"Upgrading {public_hostname} ({env})")
    ansible(env, host, public_hostname, tags="provision-update-packages")


def remove_build_dir():
    printer.warning("Removing build directory...", end="")
    c.local("rm -rf build")
    printer.success("Done")


@command
def prepare(
    env,
    host,
    public_hostname,
    version=None,
    provision_=False,
    clean_: arg(help="Remove build directory? [no]") = True,
):
    """Prepare build locally for deployment."""
    version = version or c.git_version()
    tags = []
    if provision_:
        tags.append("provision")
    tags.append("prepare")

    printer.header(f"Preparing {TITLE} website version {version} for {env}")

    if clean_:
        printer.print()
        remove_build_dir()

    printer.print()

    ansible(env, host, public_hostname, tags=tags, extra_vars={"version": version})


@command
def deploy(
    env: arg(help="Build/deployment environment"),
    host: arg(help="Deployment host"),
    public_hostname: arg(help="Public-facing hostname"),
    version: arg(help="Name of version being deployed [short git hash]") = None,
    provision_: arg(help="Run provisioning steps? [no]") = False,
    prepare_: arg(
        short_option="-r",
        inverse_short_option="-R",
        help="Run local prep steps? [yes]",
    ) = True,
    clean_: arg(help="Remove build directory? [no]") = True,
    app: arg(help="Deploy app? [yes]") = True,
    static: arg(help="Deploy static files? [yes]") = True,
):
    """Deploy site."""
    version = version or c.git_version()
    bool_as_str = lambda b: "yes" if b else "no"

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

    printer.header(f"Deploying {TITLE} website version {version} to {env}")
    printer.print(f"env = {env}")
    printer.print(f"public_hostname = {public_hostname}")
    printer.print(f"version = {version}")
    printer.print(f"provision = {bool_as_str(provision_)}")
    printer.print(f"local prep = {bool_as_str(prepare_)}")
    printer.print(f"deploy app = {bool_as_str(app)}")
    printer.print(f"deploy static = {bool_as_str(static)}")

    if clean_ and prepare_:
        printer.print()
        remove_build_dir()

    printer.print()

    ansible(env, host, public_hostname, version, tags=tags, skip_tags=skip_tags)


def get_current_path():
    root = REMOTE_SITE_DIR
    readlink_result = remote(
        "readlink current",
        run_as=SITE_USER,
        stdout="capture",
    )
    current_path = readlink_result.stdout.strip()
    if not current_path:
        abort(404, f"Could not read current link in {root}")
    return current_path


@command
def clean_remote(run_as=SITE_USER, dry_run=False):
    """Clean up remote.

    Removes old deployments under the site root.

    """
    root = REMOTE_SITE_DIR
    printer.header(f"Removing old versions from {root}")
    current_path = get_current_path()
    current_version = os.path.basename(current_path)
    printer.print(f"Current path: {current_path}")
    printer.print(f"Current version: {current_version}\n")

    find_result = remote(
        f"find {root} -mindepth 1 -maxdepth 1 -type d",
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

    if paths:
        num_paths = len(paths)
        ess = "" if num_paths == 1 else "s"
        printer.print(f"Found {num_paths} old version{ess}:")
        for path in paths:
            printer.print(path)
        printer.print()
        confirm(
            f"Permanently remove {num_paths} old version{ess}?",
            abort_on_unconfirmed=True,
        )
        printer.print()
    else:
        abort(0, "No versions other than current found; nothing to do", color="warning")

    for path in paths:
        version = os.path.basename(path)

        du_result = remote(
            f"du -sh {path} | awk '{{ print $1 }}'",
            run_as=run_as,
            stdout="capture",
        )
        size = du_result.stdout.strip()

        prefix = "[DRY RUN] " if dry_run else ""
        printer.warning(f"{prefix}Removing version: {version} ({size})... ", end="")

        if not dry_run:
            remote(f"rm -r {path}", run_as=run_as)

        printer.success("Done")


@command
def push_settings(env, host):
    """Push settings for env to current deployment and restart uWSGI.

    This provides a simple way to modify production settings without
    doing a full redeployment.

    """
    current_path = get_current_path()
    app_dir = posixpath.join(current_path, "app/")
    printer.header(f"Pushing {env} settings to {host}:{app_dir}")
    sync(f"settings.{env}.toml", app_dir, host, run_as=SITE_USER)
    printer.info("Restarting uWSGI (this can take a while)...", end="")
    remote("systemctl restart uwsgi.service", sudo=True)
    printer.success("Done")


@command
def get_prod_db(host):
    """Copy remote production database to current directory.

    The current local copy, if present, will be backed up first.

    """
    file_name = "db.sqlite3"
    local_path = Path(file_name)
    if local_path.exists():
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d-%H-%M-%S")
        backup_file_name = f"db.{now}.sqlite3"
        printer.info(f"Backing up {file_name} to {backup_file_name}")
        local_path.rename(backup_file_name)
    remote_path = f"{REMOTE_SITE_DIR}/{file_name}"
    c.local(f"scp {host}:{remote_path} .")
