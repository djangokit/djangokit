import pytest
from djangokit.core.http import make_request
from djangokit.core.middleware import djangokit_middleware


@pytest.fixture
def middleware():
    return djangokit_middleware(lambda req: req)


def test_json_ext(middleware):
    path = "/docs/test.json"
    request = make_request(path=path)
    result = middleware(request)
    assert result.path == "/docs/test"
    assert result.path_info == "/docs/test"
    assert result.META["PATH_INFO"] == "/docs/test"
    assert result.headers["Accept"] == "application/json"


def test_json_ext_via_client(client):
    path = "/docs/test.json"
    response = client.get(path)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert data == {"slug": "test"}
