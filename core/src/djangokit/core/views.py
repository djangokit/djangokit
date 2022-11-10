from django.views.generic import TemplateView


class AppView(TemplateView):
    """Render React app."""

    template_name = "djangokit/app.html"
    http_method_names = ["get", "head"]
