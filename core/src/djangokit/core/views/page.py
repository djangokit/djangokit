from django.views.generic import TemplateView

from ..build import make_server_bundle, render_bundle
from ..conf import settings as dk_settings


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
            "settings": dk_settings.as_dict(),
            "react": {
                "markup": self.render(),
            },
            "page_path": self.page_path,
        }

    def render(self):
        bundle_path = make_server_bundle(self.request)
        markup = render_bundle(bundle_path)
        return markup
