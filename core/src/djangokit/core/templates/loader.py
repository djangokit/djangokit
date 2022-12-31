from django.template.loaders.app_directories import Loader as BaseLoader
from django.template.utils import get_app_template_dirs


class Loader(BaseLoader):
    """DjangoKit template loader.

    This template loader looks in both the usual `templates` directory
    and the special DjangoKit `app` directory, which contains the base
    React client and server entrypoint modules.

    The point of this is to logically separate the React entrypoint
    modules from the base HTML templates.

    """

    def get_dirs(self):
        return super().get_dirs() + get_app_template_dirs("app")
