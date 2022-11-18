from django.conf import settings
from django.views.generic import TemplateView

from ..build import build


class PageView(TemplateView):
    """Page view.

    Handles server side rendering of the React app.

    """

    page_path = None
    template_name = "djangokit/app.html"
    http_method_names = ["get", "head"]

    @property
    def extra_context(self):
        return {
            "settings": settings.DJANGOKIT,
            "react": {
                "markup": "<div>Loading...</div>",
            },
            "page_path": self.page_path,
        }

    def build(self):
        return build(request=self.request)

    def get(self, request, *args, **kwargs):
        self.build()
        return super().get(request, *args, **kwargs)
