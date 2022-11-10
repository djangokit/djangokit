from pathlib import Path
from uuid import uuid4

DOTENV_VALUES = {
    "DJANGO_SETTINGS_MODULE": "{{ cookiecutter.package_name }}.settings",
    "DEBUG": "true",
    "SECRET_KEY": f"INSECURE-DO-NOT-USE-IN-PRODUCTION-{uuid4()}",
}

DOTENV_CONTENTS = "\n".join(f'{k}="{v}"' for k, v in DOTENV_VALUES.items())

with Path(".env").open("w") as fp:
    fp.write(DOTENV_CONTENTS)
