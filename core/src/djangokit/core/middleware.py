import json
import posixpath

from django.conf import settings
from django.core.exceptions import BadRequest
from django.http import HttpRequest


def djangokit_middleware(get_response):
    """DjangoKit middleware.

    - Intercepts requests with a path that ends with `.json` and
      modifies them to remove the `.json` extension and set the `Accept`
      header to `application/json`.

    - Adds a `prefers_json` attribute to the request based on the
      whether the request accepts `application/json` *and* prefers it
      over HTML. This can be used, for example, in views / handlers to
      decide whether to return data or redirect.

      The request's `Accept` header needs to `application/json` for this
      to work.

    - If the request is a modifying type, adds a `data` attribute to the
      request. The data will be extracted from `request.POST` or
      `request.body` (as JSON) depending on the `Content-Type` header.

    """
    dk_settings = settings.DJANGOKIT
    intercept_extensions = dk_settings.intercept_extensions
    methods_with_data = ("PATCH", "POST", "PUT")

    def middleware(request: HttpRequest):
        method = request.method
        meta = request.META
        path = request.path

        if intercept_extensions:
            _, ext = posixpath.splitext(path)

        if (
            intercept_extensions
            and method in ("GET", "HEAD")
            and ext in intercept_extensions
        ):
            j = -len(ext)
            request.path = path[:j]
            request.path_info = request.path_info[:j]
            meta["HTTP_ACCEPT"] = intercept_extensions[ext]
            meta["PATH_INFO"] = request.META["PATH_INFO"][:j]

        accept = meta.get("HTTP_ACCEPT", "*/*")
        request.prefers_json = accept == "application/json"

        # Add data attribute when appropriate
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
