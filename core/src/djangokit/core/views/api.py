from functools import cached_property
from typing import Dict

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpResponse
from django.views.generic import View

from ..http import JsonResponse


class ApiView(View):
    """API view.

    Handles API routes.

    """

    api_module = None

    @cached_property
    def allowed_methods(self) -> Dict[str, object]:
        """Get allowed methods for API view.

        The allowed methods for an API view are determined by the
        handler functions defined in the configured API module.

        Returns a dict mapping allowed method names to their
        corresponding API handlers.

        """
        if self.api_module is None:
            raise ImproperlyConfigured(
                "Class attribute api_module must be set for ApiView"
            )
        methods = {}
        has_get = False
        has_head = False
        has_options = False
        for name in dir(self.api_module):
            if name in View.http_method_names:
                methods[name] = getattr(self.api_module, name)
                if name == "get":
                    has_get = True
                elif name == "head":
                    has_head = True
                elif name == "options":
                    has_options = True
        if has_get and not has_head:
            methods["head"] = methods["get"]
        if not has_options:
            methods["options"] = self.options
        return methods

    def dispatch(self, request, *args, **kwargs):
        """Dispatch request to API handler.

        API handlers can return one of the following:

        1. A dict or a Model instance, which will be converted to JSON
        2. An HTTP status code (int), which will be converted to a JSON
           response with the specified status code
        3. A status code *and* a dict or Model instance, which will be
           converted to a JSON response with the specified status code
           and data
        4. A status code *and* a string, which will be converted to a
           response with the specified status code and body
        5. None, which will be converted to a 204 No Content response
        6. A Django response object when more control is needed over the
           response

        If there's no API handler corresponding to the request's method,
        a 405 response will be returned.

        """
        method = request.method.lower()

        if method not in self.allowed_methods:
            return self.http_method_not_allowed(request, *args, **kwargs)

        handler = self.allowed_methods[method]
        result = handler(request, *args, **kwargs)

        if result is None:
            return HttpResponse(204)

        # XXX: Most common case?
        if isinstance(result, (dict, models.Model)):
            return JsonResponse(result)

        if isinstance(result, int):
            return JsonResponse({}, status=result)

        if isinstance(result, tuple):
            if len(result) != 2:
                raise TypeError(
                    f"Handler returned tuple with unexpected length {len(result)} "
                    "(expected 2)"
                )

            status, data = result

            if not isinstance(status, int):
                raise TypeError(
                    f"Handler returned unexpected HTTP status type {type(status)} "
                    "(expected int)"
                )

            if isinstance(data, (dict, models.Model)):
                return JsonResponse(data, status=status)

            if isinstance(data, str):
                return HttpResponse(data, status=status)

            raise TypeError(
                f"Handler returned unexpected data type {type(data)} "
                "(expected dict, Model, or str)"
            )

        # XXX: Least common case?
        if isinstance(result, HttpResponse):
            return result

        raise TypeError(
            f"Handler returned unexpected object type {type(result)} "
            "(expected dict, Model, int, Tuple[int, dict], "
            "Tuple[int, Model], None or HttpResponse)."
        )
