from django.conf import settings
from django.views.generic import TemplateView

from ..build import build
from ..conf import settings as dk_settings


class PageView(TemplateView):
    """Page view.

    Handles server side rendering of the React app.

    """

    page_path = None
    template_name = "djangokit/app.html"
    http_method_names = ["get", "head"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_info = None

    @property
    def extra_context(self):
        return {
            "settings": dk_settings.as_dict(),
            "react": {
                "markup": self.build_info.markup,
            },
            "page_path": self.page_path,
        }

    def build(self):
        self.build_info = build(minify=not settings.DEBUG, request=self.request)

    def get(self, request, *args, **kwargs):
        self.build()
        return super().get(request, *args, **kwargs)
