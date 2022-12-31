from pathlib import Path
from uuid import uuid4

import toml

DJANGO_SETTINGS = {
    "DEBUG": True,
    "SECRET_KEY": f"INSECURE-DEV-KEY-{uuid4()}",
}

with Path("settings.development.toml").open("w") as fp:
    fp.write("[django]\n")
    fp.write(toml.dumps(DJANGO_SETTINGS))
