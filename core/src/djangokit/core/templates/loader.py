from django.template.loaders.app_directories import Loader as BaseLoader
from django.template.utils import get_app_template_dirs


class Loader(BaseLoader):
    """DjangoKit template loader.

    This template loader looks in both the usual `templates` directory
    and the app's `routes` directory.

    """

    def get_dirs(self):
        return super().get_dirs() + get_app_template_dirs("routes")
