from django.shortcuts import get_object_or_404

from ..models import Page


def get(_request):
    home_page = get_object_or_404(Page, slug="home")
    return home_page.as_dict()
