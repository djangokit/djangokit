from django.conf import settings
from django.test import SimpleTestCase


class TestConf(SimpleTestCase):
    def test_get_known_setting(self):
        package = settings.DJANGOKIT.package
        self.assertEqual(package, "djangokit.core.test")

    def test_get_unknown_setting(self):
        with self.assertRaises(AttributeError):
            settings.DJANGOKIT.unknown
