from functools import cached_property
from typing import Dict

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, JsonResponse
from django.views.generic import View


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

        1. A dict, which will be converted to JSON
        2. None, which will be converted to a 204 No Content response
        3. A Django response object when more control is needed over the
           response

        If there's no API handler corresponding to the request's method,
        a 405 response will be returned.

        """
        method = request.method.lower()
        handler = self.allowed_methods.get(method)

        if not handler:
            return self.http_method_not_allowed(request, *args, **kwargs)

        result = handler(request, *args, **kwargs)

        if result is None:
            return HttpResponse(204)

        if not isinstance(result, HttpResponse):
            result = JsonResponse(result)

        return result
