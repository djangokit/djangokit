import dataclasses

from django.apps import AppConfig
from django.conf import settings
from django.core import checks

from .conf import Settings


class DjangoKitConfig(AppConfig):
    default = True
    name = "djangokit.core"
    verbose_name = "DjangoKit"


@checks.register()
def check_settings(**kwargs):
    # 1. Check for required settings
    # 2. Ensure settings are of correct type
    # 3. Check for unknown settings
    errors = []
    dk_settings = settings.DJANGOKIT
    fields = dataclasses.fields(Settings)
    fields = {field.name: field for field in fields}

    for name, field in fields.items():
        is_required = field.default is dataclasses.MISSING

        if name in dk_settings:
            value = dk_settings[name]
            if not isinstance(value, field.type):
                expected_type = field.type.__name__
                got_type = value.__class__.__name__
                errors.append(
                    checks.Error(
                        f"DjangoKit setting {name} has incorrect type: "
                        f"expected {expected_type}; got {got_type}",
                        id="djangokit.E002",
                    )
                )
        elif is_required:
            errors.append(
                checks.Error(
                    f"DjangoKit setting is required: {name}",
                    id="djangokit.E001",
                )
            )

    for name in dk_settings:
        if name not in fields:
            errors.append(
                checks.Error(
                    f"Unknown DjangoKit setting: {name}",
                    id="djangokit.E003",
                )
            )

    return errors
