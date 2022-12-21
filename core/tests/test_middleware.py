from django.test import Client, SimpleTestCase

from djangokit.core.http import make_request
from djangokit.core.middleware import djangokit_middleware


class TestMiddleware(SimpleTestCase):
    def setUp(self):
        self.middleware = djangokit_middleware(lambda req: req)
        self.client = Client()

    def test_json_ext(self):
        path = "/docs/test.json"
        request = make_request(path=path)
        result = self.middleware(request)
        self.assertEqual(result.path, "/docs/test")
        self.assertEqual(result.path_info, "/docs/test")
        self.assertEqual(result.META["PATH_INFO"], "/docs/test")
        self.assertEqual(result.headers["Accept"], "application/json")

    def test_json_ext_via_client(self):
        path = "/docs/test.json"
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(data, {"slug": "test"})
