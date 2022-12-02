from django.views.generic import TemplateView

from ..build import make_server_bundle, render_bundle
from ..conf import settings


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
            "settings": settings.as_dict(),
            "markup": self.render(),
            "page_path": self.page_path,
        }

    def render(self):
        if not settings.ssr:
            return "Loading..."
        chdir = None
        bundle = make_server_bundle(
            self.request,
            minify=False,
            source_map=False,
            quiet=True,
            chdir=settings.static_build_dir,
            return_proc=True,
        )
        markup = render_bundle(bundle, chdir=chdir)
        return markup
