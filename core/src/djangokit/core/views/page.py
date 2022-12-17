import json
import logging
import os
from functools import cached_property, lru_cache
from hashlib import sha1

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
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

    @cached_property
    def extra_context(self):
        markup = self.render()
        return {
            "settings": settings.DJANGOKIT,
            "markup": markup,
            "page_path": self.page_path,
        }

    def render(self) -> str:
        request: HttpRequest = self.request

        if not settings.DJANGOKIT.ssr:
            return self.render_loading()

        # Do CSR only for logged-in users.
        #
        # XXX: This is mainly to avoid issues with React SSR hydration.
        #      The issue is that server rendered markup includes the
        #      current user data but on the client the page is hydrated
        #      *without* the user data present.
        if request.user.is_authenticated:
            return ""

        return render(request)

    def render_loading(self):
        return render_to_string(
            "djangokit/_loading.html",
            context={"settings": settings.DJANGOKIT},
            request=self.request,
        )


def render(request, bundle_name="build/server.bundle.js") -> str:
    """Render markup from server bundle and cache result."""
    dk_settings = settings.DJANGOKIT
    bundle_path = get_ssr_bundle_path(bundle_name)

    masked_csrf_token = csrf.get_token(request)
    csrf_token = csrf._unmask_cipher_token(masked_csrf_token)
    current_user_data = dk_settings.current_user_serializer(request.user)
    current_user_json = json.dumps(current_user_data)
    argv = [request.path, csrf_token, current_user_json]

    key = ":".join((bundle_path, *argv))
    key = sha1(key.encode("utf-8")).hexdigest()
    result = cache.get(key)

    if result is None:
        result = run_bundle(bundle_path, argv)
        cache.set(key, result, None)

    return result


@lru_cache(maxsize=None)
def get_ssr_bundle_path(bundle_name) -> str:
    # NOTE: This path never changes for a given deployment/version, so
    #       we only need to look it up once.
    if os.getenv("ENV") == "production":
        bundle_path = staticfiles_storage.path(bundle_name)
        if os.path.exists(bundle_path):
            return bundle_path
        raise FileNotFoundError(f"SSR bundle path does not exist: {bundle_path}")
    else:
        bundle_path = find(bundle_name)
        if bundle_path:
            return bundle_path
        raise FileNotFoundError(
            f"Could not find static file for SSR bundle: {bundle_name}"
        )
