import json

from django.core.exceptions import BadRequest
from django.http import HttpRequest


def djangokit_middleware(get_response):
    """DjangoKit middleware.

    - Adds an `is_fetch` attribute to the request so that it's easy to
      tell if it was made via `fetch()` rather than via a form. This can
      be used in views / API handlers to decide whether to redirect.

      When making requests, the `X-HTTP-Requested-With` header needs to
      be set to `fetch` or `XMLHttpRequest` for this to work.

    - If the request is a modifying type, adds a `data` attribute to the
      request. The data will be extracted from `request.POST` or
      `request.body` (as JSON) depending on the `Content-Type` header.

    """
    fetch_types = ("fetch", "XMLHttpRequest")
    methods_with_data = ("PATCH", "POST", "PUT")

    def middleware(request: HttpRequest):
        # Add is_fetch attribute
        requested_with = request.META.get("HTTP_X_REQUESTED_WITH")
        is_fetch = requested_with and requested_with in fetch_types
        request.is_fetch = is_fetch

        # Add data attribute when appropriate
        method = request.method
        if method in methods_with_data:
            content_type = request.content_type
            if content_type == "application/x-www-form-urlencoded":
                request.data = request.POST
            elif content_type == "application/json":
                try:
                    request.data = json.loads(request.body)
                except ValueError:
                    raise BadRequest("Could not parse JSON from request body.")
            else:
                raise BadRequest(
                    f"Unexpected content type for {method} request: "
                    f"{content_type}; expected application/x-www-form-urlencoded "
                    f"or application/json."
                )

        response = get_response(request)
        return response

    return middleware
