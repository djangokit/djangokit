from djangokit.core.build import build

from .app import app
from .django import configure_settings_module, run_django_command


@app.command(name="build")
def build_command(dotenv_path: str = ".env", collect: bool = True):
    configure_settings_module(dotenv_path=dotenv_path)

    build()

    if collect:
        run_django_command("collectstatic")
