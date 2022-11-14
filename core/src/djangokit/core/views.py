from django.views.generic import TemplateView, View


class PageView(TemplateView):

    page_path = None
    template_name = "djangokit/app.html"
    http_method_names = ["get", "head"]


class ApiView(View):

    pass
