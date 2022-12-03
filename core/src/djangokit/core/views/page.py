import json
import logging
import os

from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.middleware import csrf
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from ..build import run_bundle
from ..conf import settings

log = logging.getLogger(__name__)


class PageView(TemplateView):
    """Page view.

    Handles server side rendering of the React app.

    """

    page_path = None
    template_name = "djangokit/app.html"
    http_method_names = ["get", "head"]

    @property
    def extra_context(self):
        markup = self.render()
        return {
            "settings": settings.as_dict(),
            "markup": markup,
            "page_path": self.page_path,
        }

    def render(self):
        request = self.request

        if request.user.is_authenticated:
            return ""

        if not settings.ssr:
            return self.render_loading()

        bundle_name = "build/server.bundle.js"

        if os.getenv("ENV") == "production":
            bundle_path = staticfiles_storage.path(bundle_name)
            if not os.path.exists(bundle_path):
                log.error("SSR bundle path does not exist: %s", bundle_path)
                return self.render_loading()
        else:
            bundle_path = find(bundle_name)
            if not bundle_path:
                log.error("Could not find static file for SSR bundle: %s", bundle_name)
                return self.render_loading()

        csrf_token = csrf.get_token(request)
        current_user_data = settings.current_user_serializer(request.user)
        current_user_data = json.dumps(current_user_data)
        argv = [request.path, csrf_token, current_user_data]

        log.info("Running SSR bundle from static file: %s", bundle_name)
        return run_bundle(bundle_path, argv=argv)

    def render_loading(self):
        return render_to_string(
            "djangokit/_loading.html",
            context={"settings": settings},
            request=self.request,
        )
