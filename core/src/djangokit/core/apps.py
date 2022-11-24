from django.apps import AppConfig
from django.core import checks

from .checks import CHECKS


class DjangoKitCoreConfig(AppConfig):
    default = True
    name = "djangokit.core"
    verbose_name = "DjangoKit Core"

    def ready(self):
        for check in CHECKS:
            checks.register(check)
