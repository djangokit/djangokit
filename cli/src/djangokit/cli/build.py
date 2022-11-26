from django.http import HttpRequest
from djangokit.core.build import build
from djangokit.core.render import render

from .app import app, state
from .django import configure_settings_module


@app.command(name="build")
def build_command(client: bool = True, server: bool = True):
    """Build & collect static files"""
    configure_settings_module()

    if client:
        build_args = {}
        if state.env == "production":
            build_args["minify"] = True
        build(build_args)

    if server:
        request = HttpRequest()
        request.path = "/"
        request.path_info = "/"
        render(request)
