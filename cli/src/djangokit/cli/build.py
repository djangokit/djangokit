from djangokit.core.build import build

from .app import app
from .django import configure_settings_module


@app.command(name="build")
def build_command(minify: bool = True):
    """Build & collect static files"""
    configure_settings_module()
    build(minify=minify)
