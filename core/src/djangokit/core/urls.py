from django.contrib import admin
from django.http import HttpResponseServerError
from django.template import loader
from django.urls import include, path
from django.views.defaults import ERROR_500_TEMPLATE_NAME, server_error

from .conf import settings
from .routes import get_route_urls

urlpatterns = [
    path("", include(get_route_urls())),
    path("$admin/", admin.site.urls),
]


def handler500(request, template_name=ERROR_500_TEMPLATE_NAME):
    try:
        template = loader.get_template(template_name)
        context = {
            "status_code": 500,
            "settings": settings,
        }
        content = template.render(context, request)
        return HttpResponseServerError(content)
    except Exception as exc:
        import sys

        print(exc, file=sys.stderr)
        # XXX: Bail out to Django default handler if rendering fails.
        return server_error(request)
