import json
import logging
import os
from functools import lru_cache
from typing import Optional

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpRequest
from django.middleware import csrf
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from ..build import run_bundle

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
            "settings": settings.DJANGOKIT,
            "markup": markup,
            "page_path": self.page_path,
        }

    def render(self) -> str:
        request: HttpRequest = self.request

        # Do CSR only for logged-in users.
        #
        # XXX: This is mainly to avoid issues with React SSR hydration.
        #      The issue is that server rendered markup includes the
        #      current user data but on the client the page is hydrated
        #      *without* the user data present.
        if request.user.is_authenticated:
            return ""

        if not settings.DJANGOKIT.ssr:
            return self.render_loading()

        bundle_name = "build/server.bundle.js"
        bundle_path = get_ssr_bundle_path(bundle_name)

        if bundle_path is None:
            return self.render_loading()

        csrf_token = csrf.get_token(request)
        current_user_data = settings.DJANGOKIT.current_user_serializer_obj(request.user)
        current_user_json = json.dumps(current_user_data)
        argv = [request.path, csrf_token, current_user_json]

        log.info("Running SSR bundle from static file: %s", bundle_name)
        return run_bundle(bundle_path, argv)

    def render_loading(self):
        return render_to_string(
            "djangokit/_loading.html",
            context={"settings": settings.DJANGOKIT},
            request=self.request,
        )


@lru_cache(maxsize=None)
def get_ssr_bundle_path(bundle_name: str) -> Optional[str]:
    if os.getenv("ENV") == "production":
        bundle_path = staticfiles_storage.path(bundle_name)
        if os.path.exists(bundle_path):
            return bundle_path
        log.error("SSR bundle path does not exist: %s", bundle_path)
    else:
        bundle_path = find(bundle_name)
        if bundle_path:
            return bundle_path
        log.error("Could not find static file for SSR bundle: %s", bundle_name)
    return None
