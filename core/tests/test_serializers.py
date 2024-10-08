import pytest

from djangokit.core.serializers import dump_json
from djangokit.core.test.models.page import Page


def test_dump_model_instance():
    dump_json(Page(title="Page 1", slug="page-1", content="Content 1"))


@pytest.mark.django_db
def test_dump_queryset():
    dump_json(Page.objects.all())


def test_dump_dict_with_model_instances():
    dump_json(
        {
            "1": Page(title="Page 1", slug="page-1", content="Content 1"),
            "2": Page(title="Page 2", slug="page-2", content="Content 2"),
            "3": Page(title="Page 3", slug="page-3", content="Content 3"),
            "pages": [
                Page(title="Page 1", slug="page-1", content="Content 1"),
                Page(title="Page 2", slug="page-2", content="Content 2"),
                Page(title="Page 3", slug="page-3", content="Content 3"),
            ],
        }
    )


def test_dump_list_of_model_instances():
    dump_json(
        [
            Page(title="Page 1", slug="page-1", content="Content 1"),
            Page(title="Page 2", slug="page-2", content="Content 2"),
            Page(title="Page 3", slug="page-3", content="Content 3"),
            {
                "1": Page(title="Page 1", slug="page-1", content="Content 1"),
                "2": Page(title="Page 2", slug="page-2", content="Content 2"),
                "3": Page(title="Page 3", slug="page-3", content="Content 3"),
            },
        ]
    )
