import logging

from django.http import HttpResponseServerError
from django.template import loader
from django.views import defaults

from ..conf import settings

log = logging.getLogger(__name__)

TEMPLATE_NAME = "djangokit/error.html"


def bad_request(request, exception, template_name=TEMPLATE_NAME):
    return generic_error(request, exception, 400, template_name)


def permission_denied(request, exception, template_name=TEMPLATE_NAME):
    return generic_error(request, exception, 403, template_name)


def page_not_found(request, exception, template_name=TEMPLATE_NAME):
    return generic_error(request, exception, 404, template_name)


def server_error(request, template_name=TEMPLATE_NAME):
    return generic_error(request, None, 500, template_name)


def generic_error(request, exception, status_code, template_name=TEMPLATE_NAME):
    try:
        template = loader.get_template(template_name)
        context = {
            "status_code": status_code,
            "exception": exception,
            "settings": settings,
        }
        content = template.render(context, request)
        return HttpResponseServerError(content)
    except Exception:
        # XXX: Bail out to Django default handler if rendering fails.
        log.exception(
            f"Failed to render error template for %s response: %s.",
            status_code,
            template_name,
        )
        if status_code in (400, 403, 404):
            return defaults.bad_request(request, exception, template_name)
        return defaults.server_error(request)
