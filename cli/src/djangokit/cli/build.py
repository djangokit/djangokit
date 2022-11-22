from djangokit.core.build import build

from .app import app
from .django import configure_settings_module, run_django_command


@app.command(name="build")
def build_command(collect: bool = True):
    """Build & collect static files"""
    configure_settings_module()

    build()

    if collect:
        run_django_command("collectstatic")
