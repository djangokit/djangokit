from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from markdown import markdown

from ..models import Page


def get(_request):
    page = get_object_or_404(Page, slug="home")
    data = model_to_dict(page)
    data["lead"] = markdown(data["lead"])
    data["content"] = markdown(data["content"])
    return data
